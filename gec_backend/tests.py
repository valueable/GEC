from django.test import TestCase
from gector import predict
# Create your tests here.

sentences = []
sentence = "She see Tom is catched by policeman in park at last night."
sentences.append(sentence)
sentences.append("i likes running. reading and playying fottball")
sentences.append("I am a stdent.")
sentences.append("A ten years old boy go school")
correctDic, notes, dics, cnt, use_count = predict.predict_for_sentence(sentences, [])
print(correctDic)
print(notes)
print(dics)
print(use_count)