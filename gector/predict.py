# -*- coding:GBK -*-
import sys
import argparse
import time
from gector.utils.helpers import read_lines
from gector.gector.gec_model import GecBERTModel
from spellchecker import SpellChecker



# 对目标文件进行预测 返回改错个数以及更改后的句子
def predict_for_file(input_file, output_file, model, spell, batch_size=32):
    test_data = read_lines(input_file)
    predictions = []
    cnt_corrections = 0
    batch = []
    dic = {}
    labels = set()
    idx = 0
    for sent in test_data:
        batch.append(sent.split())
        if len(batch) == batch_size:
            preds, cnt, labels, _ = model.handle_batch(batch, spell)
            predictions.extend(preds)
            cnt_corrections += cnt
            batch = []
    if batch:
        preds, cnt, labels, _ = model.handle_batch(batch, spell)
        predictions.extend(preds)
        cnt_corrections += cnt
    for sentence in test_data:
        dic[sentence] = " ".join(predictions[idx])
        idx += 1
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join([" ".join(x) for x in predictions]) + '\n')
    return cnt_corrections, dic, labels


def predict_for_sentence(sentences, wordList):
    # 准备当作后端接口
    model_path = 'E://pycharm//gector//models//pretrained_gectors//xlnet_0_gector.th'
    vocab_path = 'E://pycharm//gector//data//output_vocabulary'
    model = GecBERTModel(vocab_path=vocab_path,
                         model_paths=[model_path],
                         max_len=50, min_len=3,
                         iterations=5,
                         min_error_probability=0.0,
                         min_probability=0.0,
                         lowercase_tokens=0,
                         model_name='xlnet',
                         special_tokens_fix=0,
                         log=False,
                         confidence=0,
                         is_ensemble=0,
                         )
    spell = SpellChecker()
    for word in wordList:
        spell.word_frequency.add(word)
    error_labels = set()
    batch = []
    notes = set()
    correctList = []
    use_count = 0
    for sentence in sentences:
        tokens = sentence.split()
        for tok in tokens:
            if tok in wordList:
                use_count += 1
        batch.append(tokens)
    st = time.time()
    preds, cnt, labels, dics = model.handle_batch(batch, spell)
    ed = time.time()
    for i in labels:
        error_labels.add(i)
    for idx in range(len(preds)):
        print("after correct: ", [" ".join(x) for x in preds][idx])
        print("correct errors: ", cnt)
        corr = [" ".join(x) for x in preds][idx]
        correctList.append(corr)
        print(f'inference time: {ed - st}')
    for i in error_labels:
        if i.startswith('$REPLACE'):
            notes.add("替换")
        elif i.startswith('$DELETE'):
            notes.add("删除")
        elif i.startswith('$APPEND'):
            notes.add("插入")
        elif i.startswith('$TRANSFORM'):
            label = i.split('_', 1)[1]
            if label.startswith('VERB'):
                notes.add("动词形式有误")
            elif label.startswith('AGREEMENT'):
                notes.add("请注意单复数问题")
            elif label.startswith('CASE'):
                notes.add("注意大小写")
    if 'Spell' in list(dics.keys()):
        notes.add('拼写')
    for note in notes:
        print(note)
    dics['Spell'] = list(set(dics['Spell']))
    print(dics)
    return correctList, list(notes), dics, cnt, use_count



def main(args):
    # get all paths
    # log = true 会打印具体推理信息
    model = GecBERTModel(vocab_path=args.vocab_path,
                         model_paths=args.model_path,
                         max_len=args.max_len, min_len=args.min_len,
                         iterations=args.iteration_count,
                         min_error_probability=args.min_error_probability,
                         min_probability=args.min_error_probability,
                         lowercase_tokens=args.lowercase_tokens,
                         model_name=args.transformer_model,
                         special_tokens_fix=args.special_tokens_fix,
                         log=False,
                         confidence=args.additional_confidence,
                         is_ensemble=args.is_ensemble,
                         weights=args.weights
                         )
    spell = SpellChecker()
    cnt_corrections, dic, edits = predict_for_file(args.input_file, args.output_file, model, spell,
                                       batch_size=args.batch_size)
    # evaluate with m2 or ERRANT
    if args.printable:
        for key in dic:
            print("错误句子: {key} 更正后:{value}".format(key=key, value=dic[key]))
    print(f"Produced overall corrections: {cnt_corrections}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path',
                        help='Path to the model file.', nargs='+',
                        required=True)
    parser.add_argument('--vocab_path',
                        help='Path to the model file.',
                        default='data/output_vocabulary'  # to use pretrained models
                        )
    parser.add_argument('--input_file',
                        help='Path to the evalset file',
                        required=True)
    parser.add_argument('--output_file',
                        help='Path to the output file',
                        required=True)
    parser.add_argument('--max_len',
                        type=int,
                        help='The max sentence length'
                             '(all longer will be truncated)',
                        default=50)
    parser.add_argument('--min_len',
                        type=int,
                        help='The minimum sentence length'
                             '(all longer will be returned w/o changes)',
                        default=3)
    parser.add_argument('--batch_size',
                        type=int,
                        help='The size of hidden unit cell.',
                        default=128)
    parser.add_argument('--lowercase_tokens',
                        type=int,
                        help='Whether to lowercase tokens.',
                        default=0)
    parser.add_argument('--transformer_model',
                        choices=['bert', 'gpt2', 'transformerxl', 'xlnet', 'distilbert', 'roberta', 'albert'],
                        help='Name of the transformer model.',
                        default='roberta')
    parser.add_argument('--iteration_count',
                        type=int,
                        help='The number of iterations of the model.',
                        default=5)
    parser.add_argument('--additional_confidence',
                        type=float,
                        help='How many probability to add to $KEEP token.',
                        default=0)
    parser.add_argument('--min_probability',
                        type=float,
                        default=0.0)
    parser.add_argument('--min_error_probability',
                        type=float,
                        default=0.0)
    parser.add_argument('--special_tokens_fix',
                        type=int,
                        help='Whether to fix problem with [CLS], [SEP] tokens tokenization. '
                             'For reproducing reported results it should be 0 for BERT/XLNet and 1 for RoBERTa.',
                        default=1)
    parser.add_argument('--is_ensemble',
                        type=int,
                        help='Whether to do essembling.',
                        default=0)
    parser.add_argument('--weights',
                        help='Used to calculate weighted average', nargs='+',
                        default=None)
    parser.add_argument('--printable',
                        help='whether to print the result',
                        type=int,
                        default=0)
    args = parser.parse_args()
    time_start = time.time()
    main(args)
    time_end = time.time()
    print("time in total : {times}s".format(times=time_end-time_start))

