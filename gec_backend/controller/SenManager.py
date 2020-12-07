from gec_backend.models import Sentence, User
from . import UserManager, TypeManager


def getSentencesByID(senID):
    '''
    通过句子id获取句子对象
    :param senID:
    :return: error, sentence object
    '''
    try:
        sen = Sentence.objects.get(id=senID)
    except:
        return 'wrong senID, no sentence found', None
    else:
        if sen.is_delete:
            return 'sentence is deleted', None
        else:
            return 'succeed', sen


def getSentencesByUserID(userID):
    '''
    通过userID获取句子对象列表
    :param userID:
    :return:
    '''
    err, user = UserManager.getUserByID(userID)
    if err == 'succeed':
        try:
            senList = user.sensets.all().order_by('-dateTime')
        except:
            return 'no sentence found', None
        else:
            return 'succeed', [sen for sen in senList if sen.is_delete is False]
    else:
        return 'wrong user id: ' + userID, None


def getSentencesByTypeID(typeID, userID):
    '''
    查询错误类型标签时，获取对应标签出错的句子
    :param typeID:
    :return:
    '''
    err, types = TypeManager.getTypeByID(typeID)
    if err == 'succeed':
        try:
            senList = types.err_type.all().order_by('-dateTime')
        except:
            return 'no data yet', None
        else:
            resList = []
            for sen in senList:
                if sen.user_id == userID and sen.is_delete is False:
                    resList.append(sen)
            return 'succeed', resList


def addSentences(userID, org, corr, errTypes):
    '''
    为当前用户添加句子集

    :param userID:
    :param org:
    :param corr:
    :param errType:
    :return: string
    '''
    err, user = UserManager.getUserByID(userID)
    typelist = []
    if err == 'succeed':
        newSens = Sentence(user=user, org_sen=org, corr_sen=corr, is_delete=False)
        newSens.save()
        try:
            for errtype in errTypes:
                err, type = TypeManager.addType(errtype, userID)
                typelist.append(type)
        except:
            return 'add type failed', None
        else:
            if err == 'succeed':
                for type in typelist:
                    newSens.error_type.add(type.id)
                return 'succeed', newSens
            else:
                return 'add type failed', None
    else:
        pass


def delSentences(senID):
    '''
    删除错误句子，置is_delete = True
    :param senID:
    :return:
    '''
    sen = Sentence.objects.get(id=senID)
    try:
        sen.is_delete = True
        sen.save()
    except:
        return 'del failed'
    else:
        return 'succeed'




