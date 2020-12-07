from django.test import TestCase
from gec_backend.models import Word, User
from gec_backend.controller import UserManager, WordManager

# Create your tests here.
class TestWordManager(TestCase):

    def setUp(self):
        err, self.user = UserManager.createUser("test1", "test")
        self.assertEquals(err, "succeed")

    def tests(self):
        err, user1 = UserManager.createUser("tttt", "t1")

        err, word = WordManager.addWords(self.user.id, 'fottball')
        self.assertEqual(err, 'succeed')
        err, word1 = WordManager.addWords(self.user.id, 'facebook')
        err = WordManager.updateWord(word.id, 5)
        self.assertEqual(err, 'succeed')

        err, w = WordManager.searchWord(self.user.id, "facebook")
        self.assertEqual(err, 'succeed')
        print(w.word, "====")
        err, words = WordManager.getWordByUserID(self.user.id)
        for w in words:
            print(w.word, w.use_counts)
        self.assertEqual(err, 'succeed')
        print("========")
        err = WordManager.delWord(word1.id)
        self.assertEqual(err, 'succeed')

        err, word = WordManager.addWords(user1.id, 'iphone')
        err, word = WordManager.addWords(user1.id, 'huawei')
        err = WordManager.updateWord(word.id, 10)

        err, words = WordManager.getMostUsedWord(user1.id)
        self.assertEqual(err, 'succeed')
        for word in words:
            print(word.word, word.use_counts)

        err = WordManager.delWord(word1.id)
        self.assertEqual(err, 'succeed')

        err, _ = WordManager.searchWord(self.user.id, "facebook")
        self.assertNotEqual(err, 'succeed')

        err, words = WordManager.getWordByUserID(user1.id)
        self.assertEqual(err, 'succeed')
        for w in words:
            print(w.word, w.use_counts)






