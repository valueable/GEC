from gec_backend.models import Word, User


def getWordByUserID(userID):
    '''
    返回当前用户添加的避免拼写差错的words list
    :param userID:
    :return:
    '''
    try:
        user = User.objects.get(id=userID)
    except:
        return 'fail to fetch words', []
    else:
        words = user.add_words.filter(is_delete=False).order_by('-use_counts')
        return 'succeed', words




def addWords(userID, word):
    '''
    添加避免拼写差错的word
    :param userID:
    :return:
    '''
    user = User.objects.get(id=userID)
    try:
        word = user.add_words.get(word=word)
    except:
        newword = Word(word=word, use_counts=0, is_delete=False, user=user)
        newword.save()
        return 'succeed', newword
    else:
        if word.is_delete == True:
            word.is_delete = False
            word.use_counts = 0
            word.save()
        return 'succeed', word


def searchWord(userID, wordName):
    '''
    模糊查找用户词表中的word
    :param userID:
    :param word:
    :return:
    '''
    try:
        allWords = Word.objects.filter(word__icontains=wordName).filter(user_id=userID).filter(is_delete=False)\
            .order_by('-use_counts')
    except:
        return 'failed to find word', None
    else:
        if len(allWords) == 0:
            return 'failed to find word', None
        return 'succeed', allWords


def delWord(wordID):
    '''
    删除word
    :param wordID:
    :return:
    '''
    try:
        word = Word.objects.get(id=wordID)
    except:
        print('id', wordID)
        return 'delete failed', None
    else:
        word.is_delete = True
        word.save()
        return 'succeed', word


def getMostUsedWord(userID):
    '''
    获取使用最多的单词前五
    :param userID:
    :return:
    '''
    user = User.objects.get(id=userID)
    try:
        words = user.add_words.filter(is_delete=False).order_by('-use_counts')
    except:
        return 'fail to fetch words', None
    else:
        return 'succeed', words[:5]


def updateWord(word, userID, cnt):
    try:
        err, newword = addWords(userID, word)
        newword.use_counts += cnt
        newword.save()
    except:
        return 'update failed'
    else:
        return 'succeed'


