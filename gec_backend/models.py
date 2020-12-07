from django.db import models


# Create your models here.
class User(models.Model):
    # user name
    userName = models.CharField(max_length=50)
    # 密码，存储为MD5格式
    password = models.CharField(max_length=32)
    # 头像，存储头像的url地址
    avatar = models.CharField(max_length=100, default="")
    # 邮箱，可以为空
    email = models.EmailField(default="")
    type = models.ManyToManyField('Type', related_name='errortype')


class Sentence(models.Model):
    # 所属用户id
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='sensets'
    )
    # 源句子
    org_sen = models.CharField(max_length=600)
    # 改错后句子
    corr_sen = models.CharField(max_length=600)
    # 假删除标签
    is_delete = models.BooleanField(default=False)
    # 错误类型 多对多
    error_type = models.ManyToManyField('Type', related_name='err_type')
    # 时间,其自动应用为发布的时间
    dateTime = models.DateTimeField(auto_now_add=True)


class Word(models.Model):
    # word
    word = models.CharField(max_length=100)
    # 使用次数
    use_counts = models.IntegerField(default=0)
    # fake delete
    is_delete = models.BooleanField(default=False)
    # 所属用户id
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='add_words'
    )


class Type(models.Model):
    # type
    type = models.CharField(max_length=50)
    # 出错次数
    error_counts = models.IntegerField(default=0)
