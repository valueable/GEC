from django.shortcuts import render

from gec_backend.controller import UserManager
from gec_backend.controller import WordManager
from gec_backend.controller import TypeManager
from gec_backend.controller import SenManager
from gec_backend.controller import Util

from gec_backend.models import *

from gector import predict

from django.core import serializers
import json
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

from gec_backend.models import Doc, User
import os

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

    err = UserManager.changeInfo(curUser.id, curUser.userName, password,
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
        print('!!!!!!!')
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
    print("===get User here")
    return JsonResponse(response)


def getUserNameByID(req):
    """
    根据ID获取用户名
    """
    response = {}
    userId = str(req.GET.get('userId'))
    err, user = UserManager.getUserByID(userId)
    if err == 'succeed':
        # convert queryset to json
        response['user'] = user.userName
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['err_num'] = 1
        response['msg'] = 'error'
    print("===get User here")
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


def validatepwd(req):
    response = {}
    userId = str(req.POST.get('userId'))
    pwd = (req.POST.get('pwd'))
    print("view", pwd)
    info = UserManager.isValide(userId, pwd)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['err_num'] = 1
        response['msg'] = 'error'
    return JsonResponse(response)


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
    userId = int(req.GET.get('userId'))
    orgsentences = req.GET.get('orgsentences')
    sentences = orgsentences.split('\n')
    # sentences.append(orgsentences)
    print('++++')
    _, wordList = WordManager.getWordByUserID(userId)
    wordList = [word.word for word in wordList]
    print(wordList, '-----')
    print(sentences, '-----')
    # 改错
    correctList, notes, dics, corrcnt = predict.predict_for_sentence(sentences, wordList)
    corrects = "\n".join(correctList)
    types = [str(k) for k in dics.keys() if len(dics[k]) > 0]
    # 添加改错记录， 加上对应标签
    if userId == 0:
        response['error_counts'] = corrcnt
        response['msg'] = 'succeed'
        response['err_num'] = 0
        response['correctSentenceList'] = correctList
        response['correctDetail'] = dics
        print(orgsentences)
        print(corrects)
        print(response, "=====correct sentences here but user not login=========")
        return JsonResponse(response)
    err, _, infodic = SenManager.addSentences(userId, orgsentences, corrects, types)
    if err == 'succeed':
        for t in types:
            # 更新错误类型数
            if infodic[t] == 'old':
                err = TypeManager.updateType(t, userId, len(dics[t]))
            if err != 'succeed':
                response['msg'] = 'error'
                response['err_num'] = 1
                return JsonResponse(response)
        for word in wordList:
            for l in sentences:
                if word in l:
                    print('ok')
                    err = WordManager.updateWord(word, userId, 1)
        # response['notes'] = json.dumps(notes)
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
    senId = req.GET.get('senId')
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
    userId = req.GET.get('userId')
    word = req.GET.get('word')
    word = word.split('->')[0].strip()
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
    curword = req.GET.get('wordName')
    userID = req.GET.get('userID')
    err, wordList = WordManager.getWordByUserID(userID)
    wordId = [word.id for word in wordList if word.word == curword][0]
    info, _ = WordManager.delWord(wordId)
    if info == 'succeed':
        response['msg'] = 'succeed'
        response['err_num'] = 0
    else:
        response['msg'] = 'error'
        response['err_num'] = 1
    print(response, "=====delete word here")
    return JsonResponse(response)


def uploadFile(req):
    response = {}
    curFile = req.FILES.get('file')
    userId = req.POST.get('userId')
    filedata = curFile.read()
    dir = 'F://gecwebsitefiles//uploads//' + userId + '_' + curFile.name
    corrdir = 'F://gecwebsitefiles//uploads//' + userId + '_corr_' + curFile.name
    with open(dir, 'wb') as f:
        f.write(filedata)
    cnt, _, _ = predict.predict_for_file(dir, corrdir)
    user = User.objects.get(id=userId)
    newDoc = Doc(org_doc=curFile.name, res_doc_name='corr_'+curFile.name, error_cnt=cnt, user=user)
    newDoc.save()
    response['msg'] = 'succeed'
    response['err_num'] = 0
    print('file correct finished')
    return JsonResponse(response)

def showFiles(req):
    response = {}
    userId = req.GET.get('userId')
    user = User.objects.get(id=userId)
    files = user.user_docs.all().order_by('-dateTime')
    response['msg'] = 'succeed'
    response['err_num'] = 0
    response['list'] = json.loads(serializers.serialize("json", files))
    print(response, "=====get all docs here")
    return JsonResponse(response)

def downloadFile(req):
    userId = req.GET.get('userId')
    filename = req.GET.get('filename')
    filepath = 'F://gecwebsitefiles//uploads//' + userId + '_' + filename
    print(filepath)
    file = open(filepath, 'rb')
    response = HttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=' + filename
    return response


def deleteFile(req):
    response = {}
    curfile = req.GET.get('filename')
    resfile = req.GET.get('res_doc')
    userID = req.GET.get('userID')
    user = User.objects.get(id=userID)
    file = user.user_docs.filter(org_doc=curfile)
    file.delete()
    orgfilepath = 'F://gecwebsitefiles//uploads//' + userID + '_' + curfile
    resfilepath = 'F://gecwebsitefiles//uploads//' + userID + '_' + resfile
    os.remove(orgfilepath)
    os.remove(resfilepath)
    response['msg'] = 'succeed'
    response['err_num'] = 0
    print(response, "=====delete file here")
    return JsonResponse(response)










