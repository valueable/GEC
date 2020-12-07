from gec_backend.controller import UserManager
from django.test import TestCase


# Create your tests here.
class TestUserManager(TestCase):

    def setUp(self):
        err, self.user = UserManager.createUser("test1", "test")
        self.assertEquals(err, "succeed")

    def testCreateUser(self):
        """
        test if createUser function could run correctly
        """
        err2, user2 = UserManager.createUser("test2", "aaaa")
        self.assertEquals(err2, "succeed")

    def testDelCurUser(self):
        """
        test if delUser function could run correctly
        """

        err3, user3 = UserManager.createUser("test3", "aaaa")
        self.assertEquals(err3, "succeed")

        err, user4 = UserManager.getUserByID(user3.id)
        self.assertEqual(err, "succeed")

        err = UserManager.delUserByID(self.user, user3)
        self.assertNotEqual(err, "succeed")

        err, user4 = UserManager.getUserByID(user3.id)
        self.assertEqual(err, "succeed")

        err = UserManager.delUserByID(user3.id, user3.id)
        self.assertEqual(err, "succeed")

    def testLogin(self):
        err, user1 = UserManager.login("test1", "test1")
        self.assertNotEqual(err, "succeed")

        err, user2 = UserManager.login("test1", "test")
        self.assertEqual(err, "succeed")

    def testChangePass(self):
        err = UserManager.changePassword(self.user.id, "test", "test1")
        self.assertEqual(err, "succeed")

        err, user1 = UserManager.login("test1", "test")
        self.assertNotEqual(err, "succeed")

        err, user2 = UserManager.login("test1", "test1")
        self.assertEqual(err, "succeed")

    def testChangeInfo(self):
        err = UserManager.changeInfo(self.user.id, 'liu', 'avatar', 'email@')
        err, user = UserManager.getUserByID(self.user.id)
        print(user.userName, user.avatar, user.email)
        self.assertEqual(err, "succeed")

