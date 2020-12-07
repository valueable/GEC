"""Tweaked AllenNLP dataset reader."""
import logging
import re
from random import random
from typing import Dict, List

from allennlp.common.file_utils import cached_path
from allennlp.data.dataset_readers.dataset_reader import DatasetReader
from allennlp.data.fields import TextField, SequenceLabelField, MetadataField, Field
from allennlp.data.instance import Instance
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer
from allennlp.data.tokenizers import Token
from overrides import overrides

from utils.helpers import SEQ_DELIMETERS, START_TOKEN

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

# 处理token，label，detect tags和meta data并组成field，最后形成instances
@DatasetReader.register("seq2labels_datareader")
class Seq2LabelsDatasetReader(DatasetReader):
    """
    Reads instances from a pretokenised file where each line is in the following format:

    WORD###TAG [TAB] WORD###TAG [TAB] ..... \n

    and converts it into a ``Dataset`` suitable for sequence tagging. You can also specify
    alternative delimiters in the constructor.

    Parameters
    ----------
    delimiters: ``dict``
        The dcitionary with all delimeters.
    token_indexers : ``Dict[str, TokenIndexer]``, optional (default=``{"tokens": SingleIdTokenIndexer()}``)
        We use this to define the input representation for the text.  See :class:`TokenIndexer`.
        Note that the `output` tags will always correspond to single token IDs based on how they
        are pre-tokenised in the data file.
    max_len: if set than will truncate long sentences
    """
    # fix broken sentences mostly in Lang8 匹配破碎句子如：    .aaaaa
    BROKEN_SENTENCES_REGEXP = re.compile(r'\.[a-zA-RT-Z]')

    def __init__(self,
                 token_indexers: Dict[str, TokenIndexer] = None,
                 delimeters: dict = SEQ_DELIMETERS,
                 skip_correct: bool = False,
                 skip_complex: int = 0,
                 lazy: bool = False,
                 max_len: int = None,
                 test_mode: bool = False,
                 tag_strategy: str = "keep_one",
                 tn_prob: float = 0,
                 tp_prob: float = 0,
                 broken_dot_strategy: str = "keep") -> None:
        """

        :rtype:
        """
        super().__init__(lazy)
        # 这里使用的是wordpieceindexer写的token2index方法
        self._token_indexers = token_indexers or {'tokens': SingleIdTokenIndexer()}
        self._delimeters = delimeters
        self._max_len = max_len
        self._skip_correct = skip_correct
        self._skip_complex = skip_complex
        self._tag_strategy = tag_strategy
        self._broken_dot_strategy = broken_dot_strategy
        self._test_mode = test_mode
        self._tn_prob = tn_prob
        self._tp_prob = tp_prob

    @overrides
    def _read(self, file_path):
        # if `file_path` is a URL, redirect to the cache
        # ！！！ 注意这里tag就是preprocess的所有操作labels（labels直接用opertation delimiter分隔
        file_path = cached_path(file_path)
        with open(file_path, "r") as data_file:
            logger.info("Reading instances from lines in file at: %s", file_path)
            for line in data_file:
                line = line.strip("\n")
                # skip blank and broken lines
                if not line or (not self._test_mode and self._broken_dot_strategy == 'skip'
                                and self.BROKEN_SENTENCES_REGEXP.search(line) is not None):
                    continue
                # 预处理后的文件是token+分隔符+tag 这里是要获取一个list：[[token,tag]]
                tokens_and_tags = [pair.rsplit(self._delimeters['labels'], 1)
                                   for pair in line.split(self._delimeters['tokens'])]
                try:
                    # 左边是token 右边是tags 即 keep ，delete 一类,转化成token对象
                    tokens = [Token(token) for token, tag in tokens_and_tags]
                    tags = [tag for token, tag in tokens_and_tags]
                except ValueError: # 处理没有tag的异常
                    tokens = [Token(token[0]) for token in tokens_and_tags]
                    tags = None
                # 加上 $START
                if tokens and tokens[0] != Token(START_TOKEN):
                    tokens = [Token(START_TOKEN)] + tokens
                # Token类的text属性，获取original text
                words = [x.text for x in tokens]
                if self._max_len is not None:
                    # truncate 截取
                    tokens = tokens[:self._max_len]
                    tags = None if tags is None else tags[:self._max_len]
                instance = self.text_to_instance(tokens, tags, words)
                if instance:
                    # yield 使函数可迭代并且相当于return allennlp的懒加载机制
                    yield instance

    def extract_tags(self, tags: List[str]):
        op_del = self._delimeters['operations']

        labels = [x.split(op_del) for x in tags]
        # 映射label个数的字典
        complex_flag_dict = {}
        # get flags
        for i in range(5):
            idx = i + 1
            complex_flag_dict[idx] = sum([len(x) > idx for x in labels])

        if self._tag_strategy == "keep_one":
            # get only first candidates for r_tags in right and the last for left 该策略只留第一个tag
            labels = [x[0] for x in labels]
        elif self._tag_strategy == "merge_all":
            # consider phrases as a words
            pass
        else:
            raise Exception("Incorrect tag strategy")
        # 检错tag
        detect_tags = ["CORRECT" if label == "$KEEP" else "INCORRECT" for label in labels]
        return labels, detect_tags, complex_flag_dict

    def text_to_instance(self, tokens: List[Token], tags: List[str] = None,
                         words: List[str] = None) -> Instance:  # type: ignore
        """
        We take `pre-tokenized` input here, because we don't have a tokenizer in this class.
        """
        # pylint: disable=arguments-differ
        # field 是数据instance的一部分 field需要将token fields转为token id 然后fields需要包含token id并填充
        # Field的作用是存储token的相关信息，不同的Field实现类能够存储不同任务下的数据结构信息
        fields: Dict[str, Field] = {}
        # 由于要返回 instance 所以需要用Field构造函数来初始化对应的field
        sequence = TextField(tokens, self._token_indexers)
        # token域（field）
        fields["tokens"] = sequence
        # 元数据域
        fields["metadata"] = MetadataField({"words": words})
        if tags is not None:
            labels, detect_tags, complex_flag_dict = self.extract_tags(tags)
            if self._skip_complex and complex_flag_dict[self._skip_complex] > 0:
                return None
            rnd = random()
            # skip TN
            if self._skip_correct and all(x == "CORRECT" for x in detect_tags):
                if rnd > self._tn_prob:
                    return None
            # skip TP
            else:
                if rnd > self._tp_prob:
                    return None
            # 使用allennlp的sequencelabelfield即可
            fields["labels"] = SequenceLabelField(labels, sequence,
                                                  label_namespace="labels")
            fields["d_tags"] = SequenceLabelField(detect_tags, sequence,
                                                  label_namespace="d_tags")
        return Instance(fields)
