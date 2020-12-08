"""Wrapper of AllenNLP model. Fixes errors based on model predictions"""
import logging
import os
import sys
from time import time

import torch
from allennlp.data.dataset import Batch
from allennlp.data.fields import TextField
from allennlp.data.instance import Instance
from allennlp.data.tokenizers import Token
from allennlp.data.vocabulary import Vocabulary
from allennlp.modules.text_field_embedders import BasicTextFieldEmbedder
from allennlp.nn import util

from gector.gector.bert_token_embedder import PretrainedBertEmbedder
from gector.gector.seq2labels_model import Seq2Labels
from gector.gector.wordpiece_indexer import PretrainedBertIndexer
from gector.utils.helpers import PAD, UNK, get_target_sent_by_edits, START_TOKEN, apply_reverse_transformation

from spellchecker import SpellChecker


class Speller:
    def __init__(self):
        self.spell = SpellChecker()

    def add(self, str):
        self.spell.word_frequency.add(str)

    def remove(self, str):
        self.spell.word_frequency.remove(str)

    def correction(self, str):
        return self.spell.correction(str)

logging.getLogger("werkzeug").setLevel(logging.ERROR)
logger = logging.getLogger(__file__)

spell = Speller()

# 获取预训练模型中的权重 即加载预训练模型
def get_weights_name(transformer_name, lowercase):
    if transformer_name == 'bert' and lowercase:
        #return 'bert-base-uncased'
        return 'E://pycharm//gector//models//bert-base-uncased'
    if transformer_name == 'bert' and not lowercase:
        #return 'bert-base-cased'
        return 'E://pycharm//gector//models//bert-base-cased'
    if transformer_name == 'distilbert':
        if not lowercase:
            print('Warning! This model was trained only on uncased sentences.')
        return 'distilbert-base-uncased'
    if transformer_name == 'albert':
        if not lowercase:
            print('Warning! This model was trained only on uncased sentences.')
        return 'albert-base-v1'
    if lowercase:
        print('Warning! This model was trained only on cased sentences.')
    if transformer_name == 'roberta':
        #return 'roberta-base'
        return 'E://pycharm//gector//models//roberta-base'
    if transformer_name == 'gpt2':
        return 'gpt2'
    if transformer_name == 'transformerxl':
        return 'transfo-xl-wt103'
    if transformer_name == 'xlnet':
        #return 'xlnet-base-cased'
        return 'E://pycharm//gector//models//xlnet-base-cased'

class GecBERTModel(object):
    def __init__(self, vocab_path=None, model_paths=None,
                 weights=None,
                 max_len=50,
                 min_len=3,
                 lowercase_tokens=False,
                 log=False,
                 iterations=3,
                 min_probability=0.0,
                 model_name='roberta',
                 special_tokens_fix=1,
                 is_ensemble=True,
                 min_error_probability=0.0,
                 confidence=0,
                 resolve_cycles=False,
                 ):
        # 默认model weights 为模型个数 如 [1]*3=[1,1,1] 这是ensemble中各个模型的投票权重 默认为none
        self.model_weights = list(map(float, weights)) if weights else [1] * len(model_paths)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.max_len = max_len
        self.min_len = min_len
        self.lowercase_tokens = lowercase_tokens
        self.min_probability = min_probability
        self.min_error_probability = min_error_probability
        self.vocab = Vocabulary.from_files(vocab_path)
        self.log = log
        self.iterations = iterations
        self.confidence = confidence
        self.resolve_cycles = resolve_cycles
        # set training parameters and operations

        self.indexers = []
        self.models = []
        for model_path in model_paths:
            # 如果是聚合模型
            if is_ensemble:
                model_name, special_tokens_fix = self._get_model_data(model_path)
            weights_name = get_weights_name(model_name, lowercase_tokens)
            self.indexers.append(self._get_indexer(weights_name, special_tokens_fix))
            model = Seq2Labels(vocab=self.vocab,
                               text_field_embedder=self._get_embbeder(weights_name, special_tokens_fix),
                               confidence=self.confidence
                               ).to(self.device)
            if torch.cuda.is_available():
                model.load_state_dict(torch.load(model_path))
            else:
                model.load_state_dict(torch.load(model_path,
                                                 map_location=torch.device('cpu')))
            # 相当于评估模型，不会有dropout和norm
            model.eval()
            self.models.append(model)

    @staticmethod
    def _get_model_data(model_path):
        model_name = model_path.split('/')[-1]
        tr_model, stf = model_name.split('_')[:2]
        return tr_model, int(stf)

    def _restore_model(self, input_path):
        if os.path.isdir(input_path):
            print("Model could not be restored from directory", file=sys.stderr)
            filenames = []
        else:
            filenames = [input_path]
        for model_path in filenames:
            try:
                if torch.cuda.is_available():
                    loaded_model = torch.load(model_path)
                else:
                    loaded_model = torch.load(model_path,
                                              map_location=lambda storage,
                                                                  loc: storage)
            except:
                print(f"{model_path} is not valid model", file=sys.stderr)
            own_state = self.model.state_dict()
            for name, weights in loaded_model.items():
                if name not in own_state:
                    continue
                try:
                    if len(filenames) == 1:
                        own_state[name].copy_(weights)
                    else:
                        own_state[name] += weights
                except RuntimeError:
                    continue
        print("Model is restored", file=sys.stderr)

    def predict(self, batches):
        t11 = time()
        predictions = []
        # zip将参数打包起来进入迭代
        for batch, model in zip(batches, self.models):
            batch = util.move_to_device(batch.as_tensor_dict(), 0 if torch.cuda.is_available() else -1)
            with torch.no_grad():
                prediction = model.forward(**batch)
            predictions.append(prediction)
        # 为每个句子获取最有可能的label
        preds, idx, error_probs = self._convert(predictions)
        t55 = time()
        if self.log:
            print(f"Inference time {t55 - t11}")
        return preds, idx, error_probs

    def get_token_action(self, token, index, prob, sugg_token):
        """Get lost of suggested actions for token."""
        # cases when we don't need to do anything
        if prob < self.min_probability or sugg_token in [UNK, PAD, '$KEEP']:
            return None

        if sugg_token.startswith('$REPLACE_') or sugg_token.startswith('$TRANSFORM_') or sugg_token == '$DELETE':
            start_pos = index
            end_pos = index + 1
        elif sugg_token.startswith("$APPEND_") or sugg_token.startswith("$MERGE_"):
            start_pos = index + 1
            end_pos = index + 1

        if sugg_token == "$DELETE":
            sugg_token_clear = ""
        elif sugg_token.startswith('$TRANSFORM_') or sugg_token.startswith("$MERGE_"):
            sugg_token_clear = sugg_token[:]
        else:
            sugg_token_clear = sugg_token[sugg_token.index('_') + 1:]
        # sugg_token_clear 是建议操作后面的token 如append后面的内容
        return start_pos - 1, end_pos - 1, sugg_token_clear, prob

    def _get_embbeder(self, weigths_name, special_tokens_fix):
        embedders = {'bert': PretrainedBertEmbedder(
            pretrained_model=weigths_name,
            requires_grad=False,
            top_layer_only=True,
            special_tokens_fix=special_tokens_fix)
        }
        text_field_embedder = BasicTextFieldEmbedder(
            token_embedders=embedders,
            embedder_to_indexer_map={"bert": ["bert", "bert-offsets"]},
            allow_unmatched_keys=True)
        return text_field_embedder

    def _get_indexer(self, weights_name, special_tokens_fix):
        bert_token_indexer = PretrainedBertIndexer(
            pretrained_model=weights_name,
            do_lowercase=self.lowercase_tokens,
            max_pieces_per_token=5,
            use_starting_offsets=True,
            truncate_long_sequences=True,
            special_tokens_fix=special_tokens_fix,
            is_test=True
        )
        return {'bert': bert_token_indexer}
    # 预处理token batch 返回batch实例化后的集合
    def preprocess(self, token_batch):
        seq_lens = [len(sequence) for sequence in token_batch if sequence]
        if not seq_lens:
            return []
        # 一个句子长度最多为50个word
        max_len = min(max(seq_lens), self.max_len)
        batches = []
        for indexer in self.indexers:
            batch = []
            for sequence in token_batch:
                tokens = sequence[:max_len]
                tokens = [Token(token) for token in ['$START'] + tokens]
                batch.append(Instance({'tokens': TextField(tokens, indexer)}))
            batch = Batch(batch)
            batch.index_instances(self.vocab)
            batches.append(batch)

        return batches

    # 将最大可能的预测 其对应的index以及其错误几率转成list返回
    def _convert(self, data):
        # 生成与参数维度一致的全0tensor
        all_class_probs = torch.zeros_like(data[0]['class_probabilities_labels'])
        error_probs = torch.zeros_like(data[0]['max_error_probability'])
        for output, weight in zip(data, self.model_weights):
            # 用模型权重来做inference 投票的方式
            all_class_probs += weight * output['class_probabilities_labels'] / sum(self.model_weights)
            error_probs += weight * output['max_error_probability'] / sum(self.model_weights)
        # 获取每个句子概率最大的标签
        max_vals = torch.max(all_class_probs, dim=-1)
        probs = max_vals[0].tolist()
        idx = max_vals[1].tolist()
        return probs, idx, error_probs.tolist()
    # 每个iteration更新相关记录信息
    def update_final_batch(self, final_batch, pred_ids, pred_batch,
                           prev_preds_dict):
        new_pred_ids = []
        total_updated = 0
        # enumerate 枚举 形式： id：value
        # orig 源数据 pred 预测 prev preds 上个iteration的预测
        for i, orig_id in enumerate(pred_ids):
            orig = final_batch[orig_id]
            pred = pred_batch[i]
            prev_preds = prev_preds_dict[orig_id]
            if orig != pred and pred not in prev_preds:
                final_batch[orig_id] = pred
                new_pred_ids.append(orig_id)
                prev_preds_dict[orig_id].append(pred)
                total_updated += 1
            elif orig != pred and pred in prev_preds:
                # update final batch, but stop iterations
                final_batch[orig_id] = pred
                total_updated += 1
            else:
                continue
        return final_batch, new_pred_ids, total_updated
    # 后处理batch 然后获取相应的修改操作
    def postprocess_batch(self, batch, all_probabilities, all_idxs,
                          error_probs, spell,
                          max_len=50):
        # 返回的后处理集合
        all_results = []
        all_labels = set()
        all_dics = {'APPEND': [], 'DELETE': [], 'REPLACE': [], 'CASE': [], 'VERB': [],
                    'SPLIT': [], 'AGREEMENT': [], 'Spell': []}
        # 查看allennlp相应api 参数先传入token名 然后是命名空间 这里的no-op index 即为不需要操作的token的index 的列表
        noop_index = self.vocab.get_token_index("$KEEP", "labels")
        for tokens, probabilities, idxs, error_prob in zip(batch,
                                                           all_probabilities,
                                                           all_idxs,
                                                           error_probs):
            length = min(len(tokens), max_len)
            edits = []

            # skip whole sentences if there no errors
            # index0 是$keep 即不更改
            if max(idxs) == 0:
                all_results.append(tokens)
                continue

            # skip whole sentence if probability of correctness is not high 如果出错概率小于阈值
            if error_prob < self.min_error_probability:
                all_results.append(tokens)
                continue

            for i in range(length + 1):
                # because of START token
                if i == 0:
                    token = START_TOKEN
                else:
                    token = tokens[i - 1]
                # skip if there is no error
                if idxs[i] == noop_index:
                    continue
                # 获取label
                sugg_token = self.vocab.get_token_from_index(idxs[i],
                                                             namespace='labels')
                all_labels.add(sugg_token)
                # 这里的action是返回参数的set
                action = self.get_token_action(token, i, probabilities[i],
                                               sugg_token)
                if not action:
                    tokens[i-1] = spell.correction(token)
                    if token != tokens[i-1]:
                        all_dics['Spell'].append(token + ' -> ' + tokens[i - 1])
                    continue
                edits.append(action)
                if sugg_token.startswith('$APPEND'):
                    all_dics['APPEND'].append(token+' '+sugg_token.split('_', 1)[1])
                elif sugg_token.startswith('$DELETE'):
                    all_dics['DELETE'].append(token)
                elif sugg_token.startswith('$REPLACE'):
                    all_dics['REPLACE'].append(token+' -> '+sugg_token.split('_', 1)[1])
                elif sugg_token.startswith('$TRANSFORM'):
                    modify = apply_reverse_transformation(token, sugg_token)
                    if sugg_token.startswith("$TRANSFORM_CASE"):
                        all_dics['CASE'].append(token+' -> '+modify)
                    # deal with verb
                    elif sugg_token.startswith("$TRANSFORM_VERB"):
                        all_dics['VERB'].append(token+' -> '+modify)
                    # deal with split
                    elif sugg_token.startswith("$TRANSFORM_SPLIT"):
                        all_dics['SPLIT'].append(token+' -> '+modify)
                    # deal with single/plural
                    elif sugg_token.startswith("$TRANSFORM_AGREEMENT"):
                        all_dics['AGREEMENT'].append(token+' -> '+modify)
            all_results.append(get_target_sent_by_edits(tokens, edits))
        return all_results, all_labels, all_dics

    def handle_batch(self, full_batch, spell):
        """
        Handle batch of requests.
        """
        final_batch = full_batch[:]
        batch_size = len(full_batch)
        # 此dict 为{int:list} list中是对此id下的token做出的预测（修改建议）集合
        prev_preds_dict = {i: [final_batch[i]] for i in range(len(final_batch))}
        short_ids = [i for i in range(len(full_batch))
                     if len(full_batch[i]) < self.min_len]
        # 只能给句子长度大于3的句子改错
        pred_ids = [i for i in range(len(full_batch)) if i not in short_ids]
        total_updates = 0
        # 默认5个iteration
        edits = set()
        dics = {'APPEND': [], 'DELETE': [], 'REPLACE': [], 'CASE': [], 'VERB': [], 'SPLIT': [],
                'AGREEMENT': [], 'Spell': []}
        for n_iter in range(self.iterations):
            orig_batch = [final_batch[i] for i in pred_ids]
            # token -> Token -> field -> instance -> batch 最终返回的是len(model)个batch
            sequences = self.preprocess(orig_batch)
            if not sequences:
                break
            probabilities, idxs, error_probs = self.predict(sequences)

            pred_batch, edit, all_dics = self.postprocess_batch(orig_batch, probabilities,
                                                idxs, error_probs, spell)
            for key, value in all_dics.items():
                dics[key].extend(value)
            if self.log:
                print(f"Iteration {n_iter + 1}. Predicted {round(100*len(pred_ids)/batch_size, 1)}% of sentences.")

            final_batch, pred_ids, cnt = \
                self.update_final_batch(final_batch, pred_ids, pred_batch,
                                        prev_preds_dict)
            total_updates += cnt
            if not pred_ids:
                break
            for i in edit:
                edits.add(i)
        # final_batch 列表 每个对应的index contain 对应index token的修改结果
        return final_batch, total_updates, edits, dics
