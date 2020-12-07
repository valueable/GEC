# -*- coding:GBK -*-
import sys
import argparse
import time
from utils.helpers import read_lines
from gector.gec_model import GecBERTModel
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


# ��Ŀ���ļ�����Ԥ�� ���ظĴ�����Լ����ĺ�ľ���
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


def predict_for_sentence(sentences, model, spell):
    # ׼��������˽ӿ�
    error_labels = set()
    batch = []
    notes = set()

    for sentence in sentences:
        tokens = sentence.split()
        batch.append(tokens)
    st = time.time()
    preds, cnt, labels, dics = model.handle_batch(batch, spell)
    ed = time.time()
    for i in labels:
        error_labels.add(i)
    for idx in range(len(preds)):
        print("after correct: ", [" ".join(x) for x in preds][idx])
        print("correct errors: ", cnt)
        print(f'inference time: {ed - st}')
    for i in error_labels:
        if i.startswith('$REPLACE'):
            notes.add("�滻")
        elif i.startswith('$DELETE'):
            notes.add("ɾ��")
        elif i.startswith('$APPEND'):
            notes.add("����")
        elif i.startswith('$TRANSFORM'):
            label = i.split('_', 1)[1]
            if label.startswith('VERB'):
                notes.add("������ʽ����")
            elif label.startswith('AGREEMENT'):
                notes.add("��ע�ⵥ��������")
            elif label.startswith('CASE'):
                notes.add("ע���Сд")
    if 'Spell' in list(dics.keys()):
        notes.add('ƴд')
    for note in notes:
        print(note)
    dics['Spell'] = list(set(dics['Spell']))
    print(dics)



def main(args):
    # get all paths
    # log = true ���ӡ����������Ϣ
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
    spell = Speller()
    cnt_corrections, dic, edits = predict_for_file(args.input_file, args.output_file, model, spell,
                                       batch_size=args.batch_size)
    # evaluate with m2 or ERRANT
    if args.printable:
        for key in dic:
            print("�������: {key} ������:{value}".format(key=key, value=dic[key]))
    print(f"Produced overall corrections: {cnt_corrections}")
    sentences = []
    sentence = "She see Tom is catched by policeman in park at last night."
    sentences.append(sentence)
    sentences.append("i likes running. reading and playying fottball")
    sentences.append("I am a stdent.")
    sentences.append("A ten years old boy go school")
    predict_for_sentence(sentences, model, spell)


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
