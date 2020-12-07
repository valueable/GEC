from gec_backend.models import Type, User

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



def getTypeByName(typeName):
    '''
    通过标签名获取type
    :param typeName:
    :return:
    '''
    try:
        type = Type.objects.get(type=typeName)
    except:
        return 'no type named ' + typeName, None
    else:
        return 'succeed', type


def addType(typeName, userID):
    '''
    给指定用户添加标签
    :param typeName:
    :return:
    '''
    try:
        type = Type.objects.get(type=typeName)
    except:
        # 没有则新建
        try:
            user = User.objects.get(id=userID)
            newtype = Type(type=typeName, error_counts=0)
            newtype.save()
            user.type.add(newtype)
            user.save()

        except:
            return 'add failed', None
        else:
            return 'succeed', newtype
    else:
        user = User.objects.get(id=userID)
        user.type.add(type)
        user.save()
        return 'succeed', type


def getTypeCntRank(userID):
    '''
    按照错误次数获取type
    :return:
    '''
    try:
        user = User.objects.get(id=userID)
        typeList = user.type.order_by('-error_counts')
        resList = [type for type in typeList if type.error_counts != 0]
    except:
        return 'failed to get type rank', None
    else:
        return 'succeed', resList






