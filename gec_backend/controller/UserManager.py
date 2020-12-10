from gec_backend.models import User
from gec_backend.controller import Util


def createUser(userName, password):
    '''
    描述：
    该函数传入用户名和密码，根据该用户名创建一个新用户（或者返回用户名已重复）
    返回值：
    (errorMessage: string, user: models.user)
    '''
    try:
        findUser = User.objects.get(userName=userName)
    except:
        pass
    else:
        return ("user name has already been used", None)
    print('???', Util.cryToMD5(password))
    user = User(userName=userName, password=Util.cryToMD5(password))

    user.save()
    return ("succeed", user)


def login(userName, password):
    '''
    描述：
    尝试使用该账号密码进行登录，登录成功的话返回对应的用户(models.user)，否则返回None

    返回值：
    (errorMessage: string, user: models.user)
    '''
    try:
        user = User.objects.get(userName=userName)
    except:
        print('wrong name')
        return ("no user named " + userName, None)
    else:
        realPassword = user.password
        # realPassword = user.password
        if (realPassword == Util.cryToMD5(password)):
            return ("succeed", user)
        else:
            print('wrong pwd')
            return ("wrong password for user " + userName, None)


def getUserByID(userID):
    '''
    描述：
    传给该函数一个user id，返回用户类（models.user）

    返回值：
    (errorMessage: string, user: models.user)
    '''
    try:
        user = User.objects.get(id=userID)
    except:
        return ("error ! no user with id = " + str(userID), None)
    else:
        return ("succeed", user)


def delUserByID(curUserID, delUserID):
    '''
    描述：
    该函数实现了用户的注销操作，
    注意注销操作当且仅当“当前用户==注销用户”或者“当前用户为管理员时”可用

    返回值：
    errorMessage: string
    '''
    try:
        curUser = User.objects.get(id=curUserID)
        delUser = User.objects.get(id=delUserID)
    except:
        return "can't find user with given id"
    else:
        if (curUserID != delUserID):
            return "you have no permission to del this user"
        delUser.delete()
        return "succeed"


def changeInfo(userID, userName, pwd, avatar, email):
    '''
    描述：
    更改用户user的基本信息
    返回值：
    errorMessage: string
    '''

    user = User.objects.get(id=userID)
    user.userName = userName
    user.password = Util.cryToMD5(pwd)
    user.avatar = avatar
    user.email = email
    user.save()
    return "succeed"


def changePassword(userID, oldPassword, newPassword):
    '''
    描述：
    更改用户user的密码
    （需要先验证oldPassword是否和user中保存的密码相同）
    返回值：
    errorMessage: string
    '''
    try:
        user = User.objects.get(id=userID)
    except:
        return "can't find user with given id"

    if (user.password == Util.cryToMD5(oldPassword)):
        user.password = Util.cryToMD5(newPassword)
        user.save()
        return "succeed"
    pass


def isValide(userId, pwd):
    '''
        描述：
        验证输入的密码是否正确
        返回值：
        errorMessage: string
        '''
    err, user = getUserByID(userId)
    print(user.password)
    md5pwd = Util.cryToMD5(pwd)
    print(md5pwd)
    if(md5pwd == user.password):
        return 'succeed'
    else:
        return 'failed'