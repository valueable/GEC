"""Tweaked version of corresponding AllenNLP file"""
import logging
from copy import deepcopy
from typing import Dict

import torch
import torch.nn.functional as F
from allennlp.modules.token_embedders.token_embedder import TokenEmbedder
from allennlp.nn import util
from transformers import AutoModel, PreTrainedModel

logger = logging.getLogger(__name__)


class PretrainedBertModel:
    """
    In some instances you may want to load the same BERT model twice
    (e.g. to use as a token embedder and also as a pooling layer).
    This factory provides a cache so that you don't actually have to load the model twice.
    """

    _cache: Dict[str, PreTrainedModel] = {}
    @classmethod
    # cls本质上类似于构造函数 cls是load的一个子类 可以将全局属性当作自己的属性
    def load(cls, model_name: str, cache_model: bool = True) -> PreTrainedModel:
        if model_name in cls._cache:
            return PretrainedBertModel._cache[model_name]

        model = AutoModel.from_pretrained(model_name)
        if cache_model:
            cls._cache[model_name] = model

        

        return model


class BertEmbedder(TokenEmbedder):
    """
    A ``TokenEmbedder`` that produces BERT embeddings for your tokens.
    Should be paired with a ``BertIndexer``, which produces wordpiece ids.
    Most likely you probably want to use ``PretrainedBertEmbedder``
    for one of the named pretrained models, not this base class.
    Parameters
    ----------
    bert_model: ``BertModel``
        The BERT model being wrapped.
    top_layer_only: ``bool``, optional (default = ``False``)
        If ``True``, then only return the top layer instead of apply the scalar mix.
    max_pieces : int, optional (default: 512)
        The BERT embedder uses positional embeddings and so has a corresponding
        maximum length for its input ids. Assuming the inputs are windowed
        and padded appropriately by this length, the embedder will split them into a
        large batch, feed them into BERT, and recombine the output as if it was a
        longer sequence.
    num_start_tokens : int, optional (default: 1)
        The number of starting special tokens input to BERT (usually 1, i.e., [CLS])
    num_end_tokens : int, optional (default: 1)
        The number of ending tokens input to BERT (usually 1, i.e., [SEP])
    scalar_mix_parameters: ``List[float]``, optional, (default = None)
        If not ``None``, use these scalar mix parameters to weight the representations
        produced by different layers. These mixing weights are not updated during
        training.
    """

    def __init__(
        self,
        bert_model: PreTrainedModel,
        top_layer_only: bool = False,
        max_pieces: int = 512,
        num_start_tokens: int = 1,
        num_end_tokens: int = 1
    ) -> None:
        super().__init__()
        # self.bert_model = bert_model
        # deepcopy就是单纯复制，不会因为复制对象变化而变化
        self.bert_model = deepcopy(bert_model)
        self.output_dim = bert_model.config.hidden_size
        self.max_pieces = max_pieces
        self.num_start_tokens = num_start_tokens
        self.num_end_tokens = num_end_tokens
        self._scalar_mix = None

    def set_weights(self, freeze):
        for param in self.bert_model.parameters():
            param.requires_grad = not freeze
        return

    def get_output_dim(self) -> int:
        return self.output_dim

    def forward(
        self,
        input_ids: torch.LongTensor,
        offsets: torch.LongTensor = None
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        input_ids : ``torch.LongTensor``
            The (batch_size, ..., max_sequence_length) tensor of wordpiece ids.
        offsets : ``torch.LongTensor``, optional
            The BERT embeddings are one per wordpiece. However it's possible/likely
            you might want one per original token. In that case, ``offsets``
            represents the indices of the desired wordpiece for each original token.
            Depending on how your token indexer is configured, this could be the
            position of the last wordpiece for each token, or it could be the position
            of the first wordpiece for each token.
            For example, if you had the sentence "Definitely not", and if the corresponding
            wordpieces were ["Def", "##in", "##ite", "##ly", "not"], then the input_ids
            would be 5 wordpiece ids, and the "last wordpiece" offsets would be [3, 4].
            If offsets are provided, the returned tensor will contain only the wordpiece
            embeddings at those positions, and (in particular) will contain one embedding
            per token. If offsets are not provided, the entire tensor of wordpiece embeddings
            will be returned.
        """

        batch_size, full_seq_len = input_ids.size(0), input_ids.size(-1)
        # 除了最后一个维度都取
        initial_dims = list(input_ids.shape[:-1])

        # The embedder may receive an input tensor that has a sequence length longer than can
        # be fit. In that case, we should expect the wordpiece indexer to create padded windows
        # of length `self.max_pieces` for us, and have them concatenated into one long sequence.
        # E.g., "[CLS] I went to the [SEP] [CLS] to the store to [SEP] ..."
        # We can then split the sequence into sub-sequences of that length, and concatenate them
        # along the batch dimension so we effectively have one huge batch of partial sentences.
        # This can then be fed into BERT without any sentence length issues. Keep in mind
        # that the memory consumption can dramatically increase for large batches with extremely
        # long sentences.
        needs_split = full_seq_len > self.max_pieces
        last_window_size = 0
        if needs_split:
            # Split the flattened list by the window size, `max_pieces`
            split_input_ids = list(input_ids.split(self.max_pieces, dim=-1))

            # We want all sequences to be the same length, so pad the last sequence
            # 填充列
            last_window_size = split_input_ids[-1].size(-1)
            padding_amount = self.max_pieces - last_window_size
            # 用0填充列
            split_input_ids[-1] = F.pad(split_input_ids[-1], pad=[0, padding_amount], value=0)

            # Now combine the sequences along the batch dimension 竖着拼接
            input_ids = torch.cat(split_input_ids, dim=0)
        # 即为attention机制中的pad mask 防止注意力集中在我们为了对齐而填充的0上面
        input_mask = (input_ids != 0).long()
        # input_ids may have extra dimensions, so we reshape down to 2-d
        # before calling the BERT model and then reshape back at the end.
        '''
        模型forward的返回第一个值如下
        last_hidden_state (torch.FloatTensor of shape (batch_size, sequence_length, hidden_size)) 
        – Sequence of hidden-states at the output of the last layer of the model.
        '''
        all_encoder_layers = self.bert_model(
            input_ids=util.combine_initial_dims(input_ids),
            attention_mask=util.combine_initial_dims(input_mask),
        )[0]
        # 由二维转变为三维
        if len(all_encoder_layers[0].shape) == 3:
            all_encoder_layers = torch.stack(all_encoder_layers)
        elif len(all_encoder_layers[0].shape) == 2:
            all_encoder_layers = torch.unsqueeze(all_encoder_layers, dim=0)

        if needs_split:  # 这个操作是因为输入的seq长度大于maxpiece 现在要做的是首先将其拆分为一个list的多个元素
            # First, unpack the output embeddings into one long sequence again 行拆分 列拼接
            # 这步做的是把数据拆分成一个list，list每个元素又是list，一共有seqlen/batchsize个list
            unpacked_embeddings = torch.split(all_encoder_layers, batch_size, dim=1)
            # 然后要做的是将seqlen/batchsize个list按照列进行拼接，最终形成一个list。该list维度为 batch * row/batch * col*batch
            unpacked_embeddings = torch.cat(unpacked_embeddings, dim=2)

            # Next, select indices of the sequence such that it will result in embeddings representing the original
            # sentence. To capture maximal context, the indices will be the middle part of each embedded window
            # sub-sequence (plus any leftover start and final edge windows), e.g.,
            #  0     1 2    3  4   5    6    7     8     9   10   11   12    13 14  15
            # "[CLS] I went to the very fine [SEP] [CLS] the very fine store to eat [SEP]"
            # with max_pieces = 8 should produce max context indices [2, 3, 4, 10, 11, 12] with additional start
            # and final windows with indices [0, 1] and [14, 15] respectively.

            # Find the stride as half the max pieces, ignoring the special start and end tokens
            # Calculate an offset to extract the centermost embeddings of each window
            # 寻找最能代表文本（即中间位置的跨步stride）
            stride = (self.max_pieces - self.num_start_tokens - self.num_end_tokens) // 2
            stride_offset = stride // 2 + self.num_start_tokens

            first_window = list(range(stride_offset))
            # 对应于 注释中的 2 3 4 10 11 12 表示的是一个能代表一句话的上下文窗口

            max_context_windows = [
                i
                for i in range(full_seq_len)
                if stride_offset - 1 < i % self.max_pieces < stride_offset + stride
            ]

            # Lookback what's left, unless it's the whole self.max_pieces window lookback为应该往左边查看多少个token
            if full_seq_len % self.max_pieces == 0:
                lookback = self.max_pieces
            else:
                lookback = full_seq_len % self.max_pieces
            # 确定index选择区间
            final_window_start = full_seq_len - lookback + stride_offset + stride
            final_window = list(range(final_window_start, full_seq_len))

            select_indices = first_window + max_context_windows + final_window
            # 这时候将最后一维加入list中
            initial_dims.append(len(select_indices))

            recombined_embeddings = unpacked_embeddings[:, :, select_indices]
        else:
            recombined_embeddings = all_encoder_layers

        # Recombine the outputs of all layers
        # (layers, batch_size * d1 * ... * dn, sequence_length, embedding_dim)
        # recombined = torch.cat(combined, dim=2)
        # 同上
        input_mask = (recombined_embeddings != 0).long()

        if self._scalar_mix is not None:
            mix = self._scalar_mix(recombined_embeddings, input_mask)
        else:
            mix = recombined_embeddings[-1]

        # At this point, mix is (batch_size * d1 * ... * dn, sequence_length, embedding_dim)

        if offsets is None:
            # Resize to (batch_size, d1, ..., dn, sequence_length, embedding_dim)
            dims = initial_dims if needs_split else input_ids.size()
            return util.uncombine_initial_dims(mix, dims)
        else:
            # offsets 在gec_model 中的preprocess函数里面生成的，维度为[batch_size, seq_len]
            offsets2d = util.combine_initial_dims(offsets)
            # now offsets is [batch_size, seq_len]
            range_vector = util.get_range_vector(
                offsets2d.size(0), device=util.get_device_of(mix)
            ).unsqueeze(1)
            # selected embeddings is also (batch_size * d1 * ... * dn, orig_sequence_length)
            # 这里是选择最后一列用作embed的部分
            selected_embeddings = mix[range_vector, offsets2d]
            # return the reshaped tensor of embeddings with shape (d1, ..., dn, sequence_length, embedding_dim)
            # If original size is 1-d or 2-d, return it as is.
            # 这里直接返回selected embedings
            return util.uncombine_initial_dims(selected_embeddings, offsets.size())


# @TokenEmbedder.register("bert-pretrained")
class PretrainedBertEmbedder(BertEmbedder):

    """
    Parameters
    ----------
    pretrained_model: ``str``
        Either the name of the pretrained model to use (e.g. 'bert-base-uncased'),
        or the path to the .tar.gz file with the model weights.
        If the name is a key in the list of pretrained models at
        https://github.com/huggingface/pytorch-pretrained-BERT/blob/master/pytorch_pretrained_bert/modeling.py#L41
        the corresponding path will be used; otherwise it will be interpreted as a path or URL.
    requires_grad : ``bool``, optional (default = False)
        If True, compute gradient of BERT parameters for fine tuning.
    top_layer_only: ``bool``, optional (default = ``False``)
        If ``True``, then only return the top layer instead of apply the scalar mix.
    scalar_mix_parameters: ``List[float]``, optional, (default = None)
        If not ``None``, use these scalar mix parameters to weight the representations
        produced by different layers. These mixing weights are not updated during
        training.
    """

    def __init__(
        self,
        pretrained_model: str,
        requires_grad: bool = False,
        top_layer_only: bool = False,
        special_tokens_fix: int = 0,
    ) -> None:
        model = PretrainedBertModel.load(pretrained_model)
        # 需要计算梯度则参数随train更新
        for param in model.parameters():
            param.requires_grad = requires_grad

        super().__init__(
            bert_model=model,
            top_layer_only=top_layer_only
        )
        # 针对roberta
        if special_tokens_fix:
            try:
                vocab_size = self.bert_model.embeddings.word_embeddings.num_embeddings
            except AttributeError:
                # reserve more space
                vocab_size = self.bert_model.word_embedding.num_embeddings + 5
            self.bert_model.resize_token_embeddings(vocab_size + 1)
