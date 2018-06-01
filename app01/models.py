from django.db import models
from django.contrib.auth.models import AbstractUser


class UserInfo(AbstractUser):
    """扩展用户信息表"""
    nickname = models.CharField(max_length=50, verbose_name='昵称', null=True, blank=True)
    telephone = models.CharField(max_length=11, blank=True, null=True, unique=True, verbose_name='手机号码')
    avatar = models.FileField(verbose_name='头像',upload_to='user/%Y/%m',default='static/img/default.jpg')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        db_table='用户信息'


######################### 邮箱验证码表格
from django.db import models
class EmailValidCode(models.Model):
    code=models.CharField(verbose_name='验证码',max_length=12)
    email=models.EmailField(verbose_name='邮箱',max_length=50)

    def __str__(self):
        return self.email

    class Meta:
        db_table='邮箱验证码'



class Book(models.Model):
    title = models.CharField(max_length=50,verbose_name='名称')
    price = models.FloatField(verbose_name='价格',default=0)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '书信息'
        verbose_name_plural = verbose_name
        db_table='书信息'
