from django.shortcuts import render

from gec_backend.controller import UserManager
from gec_backend.controller import WordManager
from gec_backend.controller import  TypeManager
from gec_backend.controller import SenManager
from gec_backend.controller import Util

from gec_backend.models import *

from gector import predict

from django.core import serializers
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

# Create your views here.

def getCurUserID(req):
    response = {}
    err, curUser = Util.getUserIDBySession(req)
    if err == 'succeed':
        response['userID'] = curUser
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['err_num'] = 1
        response['msg'] = 'error'
    # print(response)
    return JsonResponse(response)


def createUser(req):
    """
    创建用户
    """
    userName = str(req.POST.get('userName'))
    password = str(req.POST.get('password'))

    err, curUser = UserManager.createUser(userName, password)

    if (err != 'succeed'):
        return HttpResponse("注册失败")

    email = str(req.POST.get('email'))
    avatar = str(req.POST.get('avatar'))
    if (avatar == ""):
        avatar = "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"

    err = UserManager.changeInfo(curUser.id, curUser.userName,
                                  avatar, email)

    if (err != 'succeed'):
        return HttpResponse("注册成功!")

    ret = HttpResponse("注册成功！")

    print(Util.setUserForSession(req, curUser.id), "===set session here")
    return ret


def login(req):
    """
    登录
    """
    userName = str(req.POST.get('userName'))
    password = str(req.POST.get('password'))

    err, curUser = UserManager.login(userName, password)

    if (err != "succeed"):
        return HttpResponse(err)

    Util.setUserForSession(req, curUser.id)

    return HttpResponse(err)


def logout(req):
    """
    登出账号
    """
    Util.delUserForSession(req)

    return HttpResponse('succeed')


def getUserByID(req):
    """
    根据ID获取用户
    """
    response = {}
    userId = str(req.POST.get('userId'))
    err, user = UserManager.getUserByID(userId)
    if err == 'succeed':
        # convert queryset to json
        response['user'] = json.loads(serializers.serialize("json", [user]))
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['err_num'] = 1
        response['msg'] = 'error'
    print(response, "===get User here")
    return JsonResponse(response)


def delUserByID(req):
    """
    根据ID删除用户
    """
    userID = int(req.POST.get("userID"))

    err, curID = Util.getUserIDBySession(req)

    if (err != 'succeed'):
        return HttpResponse("请先登录")

    err, cur = UserManager.getUserByID(curID)
    if (err != 'succeed'):
        return HttpResponse("Error")

    err, user = UserManager.getUserByID(userID)
    if (err != 'succeed'):
        return HttpResponse("Error")

    if (curID != userID and not cur.isAdmin):
        return HttpResponse("权限不足")

    err = UserManager.delUserByID(curID, userID)

    if (err != 'succeed'):
        return HttpResponse('Error')

    if (curID == userID):
        Util.delUserForSession(req)

    return HttpResponse("删除成功")


def changeInfo(req):
    """
    编辑用户信息
    """
    userId = str(req.POST.get('userId'))
    nickName = str(req.POST.get('nickName'))
    userName = str(req.POST.get('userName'))
    password = str(req.POST.get('password'))
    sex = str(req.POST.get('sex'))
    print(sex)
    if (sex == "男"):
        sex = 1
    else:
        sex = 0
    email = str(req.POST.get('email'))
    avatar = str(req.POST.get('avatar'))
    if (avatar == ""):
        avatar = "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"

    err = UserManager.changeInfo(userId, userName, password, avatar, email)
    print(err)
    return HttpResponse("succeed")


def getUserSentences(req):
    '''
    获取当前用户的错句集
    '''
    userId = str(req.GET.get('userId'))
    response = {}
    info, sentences = SenManager.getSentencesByUserID(userId)
    if info == 'succeed':
        response['list'] = json.loads(serializers.serialize("json", sentences))
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====get sentence via user here")
    return JsonResponse(response)


def getSentenceByType(req):
    '''
    搜索相关标签对应的句子集
    '''
    userId = str(req.GET.get('userId'))
    typeName = str(req.GET.get('typeName'))
    response = {}
    info, sentences = SenManager.getSentencesByTypeName(typeName, userId)
    if info == 'succeed':
        response['list'] = json.loads(serializers.serialize("json", sentences))
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====get sentence via type here")
    return JsonResponse(response)


def getTypeBySentence(req):
    '''
    获取该错句集的错误type
    '''
    response = {}
    senId = req.GET.get('senId')
    info, types = TypeManager.getTypeBySentence(senId)
    if info == 'succeed':
        response['list'] = json.loads(serializers.serialize("json", types))
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====get types via sentence here")
    return JsonResponse(response)


def correctSentence(req):
    response = {}
    userId = req.POST.get('userId')
    orgsentences = req.POST.get('orgsentences')
    wordList = WordManager.getWordByUserID(userId)
    # 改错
    correctList, notes, dics, corrcnt, use_countDic = predict.predict_for_sentence(orgsentences, wordList)
    corrects = " ".join(correctList)
    types = [str(k) for k in dics.keys()]
    # 添加改错记录， 加上对应标签
    err, _ = SenManager.addSentences(userId, orgsentences, corrects, types)
    if err == 'succeed':
        for t in types:
            # 更新错误类型数
            err = TypeManager.updateType(t, userId, len(dics[t]))
            if err != 'succeed':
                response['msg'] = 'error'
                response['err_num'] = 1
                return JsonResponse(response)
        for items in use_countDic:
            info = WordManager.updateWord(items[0], userId, items[1])
            if info != 'succeed':
                response['msg'] = 'error'
                response['err_num'] = 1
                return JsonResponse(response)
        response['notes'] = notes
        response['error_counts'] = corrcnt
        response['msg'] = 'succeed'
        response['err_num'] = 0
        response['correctSentenceList'] = correctList
        response['correctDetail'] = dics
        print(response, "=====correct sentences here=========")
        return JsonResponse(response)
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
        return JsonResponse(response)


def deleteSentences(req):
    response = {}
    senId = req.POST.get('senId')
    info = SenManager.delSentences(senId)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====delete sentence via senID here")
    return JsonResponse(response)


def addWord(req):
    response = {}
    userId = req.POST.get('userId')
    word = req.POST.get('word')
    err, _ = WordManager.addWords(userId, word)
    if err == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====add words here")
    return JsonResponse(response)


def getOftenTypes(req):
    response = {}
    userId = req.GET.get('userId')
    info, typeList = TypeManager.getTypeCntRank(userId)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
        response['list'] = json.loads(serializers.serialize("json", typeList))
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====get types rank here")
    return JsonResponse(response)


def getMostUserWords(req):
    response = {}
    userId = req.GET.get('userId')
    info, wordList = WordManager.getMostUsedWord(userId)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
        response['list'] = json.loads(serializers.serialize("json", wordList))
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====get words rank here")
    return JsonResponse(response)


def searchWord(req):
    response = {}
    userId = req.POST.get('userId')
    word = req.POST.get('word')
    info, words = WordManager.searchWord(userId, word)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
        response['list'] = json.loads(serializers.serialize("json", words))
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====search words here")
    return JsonResponse(response)


def getUserVocab(req):
    response = {}
    userId = req.GET.get('userId')
    info, vocab = WordManager.getWordByUserID(userId)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
        response['list'] = json.loads(serializers.serialize("json", vocab))
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====get all words here")
    return JsonResponse(response)


def delWord(req):
    response = {}
    wordId = req.POST.get('wordId')
    info, _ = WordManager.delWord(wordId)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====delete word here")
    return JsonResponse(response)








