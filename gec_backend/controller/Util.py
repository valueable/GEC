import hashlib

def cryToMD5(str):
    '''
    描述：
    该函数接受一个字符串，返回一个MD5字符串
    返回值：
    code: string
    '''
    ret = hashlib.md5(str.encode(encoding = "UTF-8") ).hexdigest()
    return ret

def getUserIDBySession(req):
    '''
    描述：
    该函数接收当前的request，返回其对应的用户
    返回值：
    (errMessage: string, userID: int)
    '''
    userID = req.session.get('id', 0)
    if (userID == 0):
        return ("no user in this session", userID)
    else:
        return ("succeed", userID)

def setUserForSession(req, userID):
    '''
    描述：
    该函数将当前的session与当前登录的用户进行绑定
    
    返回值：
    errMessage: string
    '''
    req.session['id'] = userID
    # req.session.__setitem__('id', userID)
    return "succeed"

def delUserForSession(req):
    '''
    描述：
    该函数将当前的用户从当前session中删除
    
    返回值：
    errMessage: string
    '''
    try:
        req.session.__delitem__('id')
    except:
        return "no user in session"
    else:
        return "succeed"