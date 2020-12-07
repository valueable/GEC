from gec_backend.models import Word, User


def getWordByUserID(userID):
    '''
    返回当前用户添加的避免拼写差错的words list
    :param userID:
    :return:
    '''
    user = User.objects.get(id=userID)
    try:
        words = user.add_words.filter(is_delete=False).order_by('-use_counts')
    except:
        return 'fail to fetch words', None
    else:
        return 'succeed', words


def addWords(userID, word):
    '''
    添加避免拼写差错的word
    :param userID:
    :return:
    '''
    user = User.objects.get(id=userID)
    try:
        newword = Word(word=word, use_counts=0, is_delete=False, user=user)
        newword.save()
    except:
        return 'fail to add word', None
    else:
        return 'succeed', newword


def searchWord(userID, wordName):
    '''
    查找用户词表中的word
    :param userID:
    :param word:
    :return:
    '''
    err, words = getWordByUserID(userID)
    if err == 'succeed':
        for w in words:
            if w.word == wordName:
                return 'succeed', w
        return 'not found', None
    else:
        return 'failed to find word', None


def delWord(wordID):
    '''
    删除word
    :param wordID:
    :return:
    '''
    word = Word.objects.get(id=wordID)
    try:
        word.is_delete = True
        word.save()
    except:
        return 'delete failed'
    else:
        return 'succeed'


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


def updateWord(wordID, cnt):
    word = Word.objects.get(id=wordID)
    try:
        word.use_counts += cnt
        word.save()
    except:
        return 'update failed'
    else:
        return 'succeed'


