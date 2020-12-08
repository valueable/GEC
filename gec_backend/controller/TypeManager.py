from gec_backend.models import Type, User, Sentence

def getTypeByID(typeID):
    '''
    通过id获取type
    :param typeID:
    :return:
    '''
    try:
        types = Type.objects.get(id=typeID)
    except:
        return 'error, id not found', None
    else:
        return  'succeed', types



def getTypeByName(typeName, userID):
    '''
    通过标签名获取type
    :param typeName:
    :return:
    '''
    try:
        user = User.objects.get(id=userID)
        type = user.type.get(type=typeName)
    except:
        return 'no type named ' + typeName, None
    else:
        return 'succeed', type


def addType(typeName, userID):
    '''
    由 addsentence调用
    给指定用户添加标签
    :param typeName:
    :return:
    '''
    try:
        user = User.objects.get(id=userID)
    except:
        return 'add failed', None
    else:
        # 没有则新建
        try:
            type = user.type.get(type=typeName)
        except:
            newtype = Type(type=typeName, error_counts=1)
            newtype.save()
            user.type.add(newtype)
            user.save()
            return 'succeed', newtype
        else:
            return 'succeed', type


def updateType(typeName, userID, cnt):
    err, type = addType(typeName, userID)
    type.error_counts += cnt
    type.save()
    return 'succeed'



def getTypeCntRank(userID):
    '''
    按照错误次数获取type
    :return:
    '''
    try:
        user = User.objects.get(id=userID)
        typeList = user.type.all().order_by('-error_counts')
    except:
        return 'failed to get type rank', None
    else:
        return 'succeed', typeList

def getTypeBySentence(senID):
    '''
    通过sentence获取type
    '''
    try:
        sen = Sentence.objects.get(id=senID)
    except:
        return 'wrong sen id', None
    else:
        return 'succeed', sen.error_type.all()






