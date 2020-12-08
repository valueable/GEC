from gec_backend.controller import UserManager, SenManager, TypeManager
from django.test import TestCase


# Create your tests here.
# !!! includes test for SenManager and TypeManager
class TestSenManager(TestCase):

    def setUp(self):
        err, self.user = UserManager.createUser("test1", "test")
        self.assertEquals(err, "succeed")

    def testAddSen(self):
        """
        test if addSentences function could run correctly
        """
        print("=======  test add")
        err2, newsen = SenManager.addSentences(self.user.id, 'org sentence', 'correct sentence',
                                              ['spell', 'case', 'verb', 'replace'])
        self.assertEquals(err2, "succeed")
        for type in list(newsen.error_type.all()):
            print(type.type)
        err3, newsen = SenManager.addSentences(self.user.id, 'org sentence1', 'correct sentence1',
                                               ['spell', 'case', 'verb'])
        err4, lists = SenManager.getSentencesByUserID(self.user.id)
        self.assertEqual(err4, 'succeed')
        for l in lists:
            print(l.org_sen, l.corr_sen, l.is_delete, [t.type for t in l.error_type.all()], l.dateTime)

        err0, type = TypeManager.getTypeByName('spell', self.user.id)
        self.assertEqual(err0, 'succeed')
        print('newuser==============')
        err0, newuser = UserManager.createUser('ttt', 'ppp')
        err3, newsen = SenManager.addSentences(newuser.id, 'org sentence222', 'correct sentence222',
                                               ['spell', 'case', 'verb'])
        err, type = TypeManager.getTypeByName('spell', newuser.id)
        err5, resList = SenManager.getSentencesByTypeName('replace', self.user.id)
        self.assertEqual(err5, 'succeed')
        for l in resList:
            print(l.org_sen, l.corr_sen, l.is_delete, [t.type for t in l.error_type.all()], l.dateTime)
        err0, type = TypeManager.getTypeByName('spell', newuser.id)

        print("===")
        err = TypeManager.updateType('spell', self.user.id, 10)
        err, lists = TypeManager.getTypeCntRank(self.user.id)
        for l in lists:
            print(l.type, l.error_counts)
        print("+++")
        err, typelist = TypeManager.getTypeBySentence(newsen.id)
        for l in typelist:
            print(l.type)
    def testDel(self):
        print("=======  test delete")
        err2, newsen = SenManager.addSentences(self.user.id, 'org sentence', 'correct sentence',
                                               ['spell', 'case', 'verb', 'replace'])
        err3, newsen = SenManager.addSentences(self.user.id, 'org sentence1', 'correct sentence1',
                                               ['spell', 'case', 'verb'])

        err0, newuser = UserManager.createUser('ttt', 'ppp')
        err3, newsen1 = SenManager.addSentences(newuser.id, 'org sentence1', 'correct sentence1',
                                               ['spell', 'case', 'verb'])
        self.assertNotEqual(newsen1.id, newsen.id)
        err3 = SenManager.delSentences(newsen.id)
        self.assertEqual(err3, 'succeed')
        err4, sen = SenManager.getSentencesByID(newsen.id)
        self.assertNotEqual(err4, 'succeed')
        err4, lists = SenManager.getSentencesByUserID(newuser.id)
        self.assertEqual(err4, 'succeed')
        for l in lists:
            print(l.user.userName, l.org_sen, l.corr_sen, l.is_delete, [t.type for t in l.error_type.all()], l.dateTime)

        err4, lists = SenManager.getSentencesByUserID(self.user.id)
        self.assertEqual(err4, 'succeed')
        for l in lists:
            print(l.org_sen, l.corr_sen, l.is_delete, [t.type for t in l.error_type.all()], l.dateTime)
        err0, type = TypeManager.getTypeByName('case', self.user.id)
        print("++++")
        err5, resList = SenManager.getSentencesByTypeName('case', self.user.id)
        self.assertEqual(err5, 'succeed')
        for l in resList:
            print(l.org_sen, l.corr_sen, l.is_delete, [t.type for t in l.error_type.all()], l.dateTime)
