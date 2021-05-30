"""Tweaked AllenNLP dataset reader."""
# 基于源码sequence_tagging改动
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

from gector.utils.helpers import SEQ_DELIMETERS, START_TOKEN

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

# 处理token，label，detect tags和meta data并组成field，最后形成instances
@DatasetReader.register("seq2labels_datareader")
class Seq2LabelsDatasetReader(DatasetReader):
    """
    Reads instances from a pretokenized file where each line is in the following format:

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
    同时，datasetreader类需要重写read和text_to_instance方法，顾名思义，分别是从文件中读数据和将文本转成allennlp的instance
    工作流程如下
    1. Token(token) 包括截取
    2. Tokenfield(token, token indexer)
    3. 获取token的text(元数据)metadata，label, d_tag，将上述三个封装成field对象，然后把上述组成字典 'token' -> filed(token)
    4. 最后在封装成instance
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
        self._skip_correct = skip_correct   # 1
        self._skip_complex = skip_complex   # 0
        self._tag_strategy = tag_strategy   # keep one
        self._broken_dot_strategy = broken_dot_strategy
        self._test_mode = test_mode
        self._tn_prob = tn_prob    # 只有最后一个阶段的微调才为1，因为对应数据集存在五语法错误的数据
        self._tp_prob = tp_prob    # 一直都是1

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
                # 预处理后的文件是token+分隔符+tag 这里是要获取一个list：[[token1,tag1], [token2, tag2]...]
                tokens_and_tags = [pair.rsplit(self._delimeters['labels'], 1)
                                   for pair in line.split(self._delimeters['tokens'])]
                try:
                    # 左边是token 右边是tags 即 keep ，delete 一类,转化成token对象(allennlp 工作流程)
                    tokens = [Token(token) for token, tag in tokens_and_tags]
                    tags = [tag for token, tag in tokens_and_tags]
                except ValueError:  # 处理没有tag的异常
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
                # 封装成实例，包含tokens， label等字段
                instance = self.text_to_instance(tokens, tags, words)
                if instance:
                    # yield 使函数可迭代并且相当于return allennlp的懒加载机制
                    # 简单来说，就是当用到该instance才加载到内存，但也相当于是用时间换空间
                    yield instance

    # 新加函数
    def extract_tags(self, tags: List[str]):
        op_del = self._delimeters['operations']
        # 将多个label分开
        labels = [x.split(op_del) for x in tags]
        # 映射label个数的字典
        complex_flag_dict = {}
        # 分别统计有一个label的有多少个，有两个label的有多少个。。。直到五个
        for i in range(5):
            idx = i + 1
            complex_flag_dict[idx] = sum([len(x) > idx for x in labels])

        if self._tag_strategy == "keep_one":
            # 该策略只留第一个tag，gector使用该策略
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
        # 元数据域 即为字符串类型的token
        fields["metadata"] = MetadataField({"words": words})
        if tags is not None:
            labels, detect_tags, complex_flag_dict = self.extract_tags(tags)
            if self._skip_complex and complex_flag_dict[self._skip_complex] > 0:
                return None
            rnd = random()
            # skip TN(真实负例是指无语法错误的句子)
            if self._skip_correct and all(x == "CORRECT" for x in detect_tags):
                # 前两个阶段prob为0，所以默认跳过；最后一阶段为1，所以不可跳过
                if rnd > self._tn_prob:
                    return None
            # skip TP，gector中不允许跳过
            else:
                if rnd > self._tp_prob:
                    return None
            # 使用allennlp的sequencelabelfield即可
            fields["labels"] = SequenceLabelField(labels, sequence,
                                                  label_namespace="labels")
            fields["d_tags"] = SequenceLabelField(detect_tags, sequence,
                                                  label_namespace="d_tags")
        return Instance(fields)
