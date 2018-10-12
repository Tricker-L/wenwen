from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser
from django.utils import timezone
import hashlib
import string
import random
from django.conf import settings
SALT = getattr(settings,'EMAIL_TOKEN_SALT')
#BaseUserManager -->管理器object
#AbstractBaseUser -> 模型类

class MyUserManager(BaseUserManager):
    def create_user(self,username,email,password=None):
        if not email:
            raise ValueError('请输入邮箱')
        if not username:
            raise ValueError('请输入用户名')
        now = timezone.now()
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            date_joined=now,
            last_login=now
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username,email,password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class Member(AbstractBaseUser):
    #用户表
    email = models.EmailField(verbose_name='邮箱',max_length=255,unique=True)
    username = models.CharField(verbose_name='用户名',max_length=16,unique=True)
    weibo_id = models.CharField(verbose_name='新浪微博',max_length=30,blank=True)
    blog = models.CharField(verbose_name='个人网站',max_length=200,blank=True)
    location = models.CharField(verbose_name='城市',max_length=10,blank=True)
    profile = models.CharField(verbose_name='个人简介',max_length=140,blank=True)
    avatar = models.CharField(verbose_name='头像',max_length=128,blank=True)
    au = models.IntegerField(verbose_name='活跃度',default=0)
    last_ip = models.GenericIPAddressField(verbose_name='上次访问的IP',default='0.0.0.0')
    email_verified = models.BooleanField(verbose_name='邮箱是否验证',default=False)
    date_joined = models.DateTimeField(verbose_name='用户注册时间',default=timezone.now)
    topic_num = models.IntegerField(verbose_name='帖子数',default=0)
    comment_num = models.IntegerField(verbose_name='评论数', default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'#使用email作为用户的用户名
    REQUIRED_FIELDS = ['email']#定义username作为当前的唯一标识符
    objects = MyUserManager()

    def __str__(self):
        return self.username

    def comment_num_add(self):
        self.comment_num += 1
        return self.comment_num

    def topic_num_add(self):
        self.topic_num += 1
        return self.topic_num

    def calculate_au(self):
        self.au = self.topic_num * 5 + self.comment_num * 1
        return self.au

    def is_email_verified(self):
        return self.email_verified

    def get_weibo(self):
        return self.weibo_id

    def get_email(self):
        return self.email

    def get_username(self):
        return self.username

    #重写父类的属性，以下五个方法必须重写
    def get_full_name(self):
        # 返回first_name加上last_name ，
        # 中间加上一个空格，如果重新设置first_name及last_name字段，
        # 这个默认函数需要重新给定返回值。
        return self.email

    def get_short_name(self):
        #一个短的且非正式用户的标识符，返回first_name，
        # 如果重新设置相关字段，去掉了first_name，必须重新给定这个函数的返回值
        return self.username

    def has_perm(self,perm,obj=None):
        #用户是否具有某个权限，如果给定obj，则需要根据特定对象实例检查权限。
        return True

    def has_module_perms(self,app_label):
        #如果用户有权访问给定应用中的模型，则返回True，
        # 如果has_perm，has_module_perms都设置为True，可以让用户访问任一APP。
        return True

    @property
    def is_staff(self):
        return self.is_admin

class Follower(models.Model):
    user_a = models.ForeignKey(Member,related_name='user_a',verbose_name='偶像',on_delete=models.CASCADE)
    user_b = models.ForeignKey(Member, related_name='user_b', verbose_name='粉丝',on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_a','user_b')

    def __str__(self):
        return "%s following %s"%(self.user_a,self.user_b)

class EmailVerified(models.Model):
    #邮箱验证表
    user = models.OneToOneField(Member,related_name='user',verbose_name='用户',on_delete=models.CASCADE)
    token = models.CharField(verbose_name='email验证token',max_length=32,default=None)
    timestamp = models.DateTimeField(default=timezone.now,verbose_name='令牌创建时间')

    def __str__(self):
        return '%s@%s'%(self.user,self.token)

    def generate_token(self):
        #令牌生成
        year = self.timestamp.year
        month = self.timestamp.month
        day = self.timestamp.day
        date = "%s-%s-%s"%(year,month,day)
        token = hashlib.md5((self.ran_str()+date).encode('utf-8')).hexdigest()
        return token

    def ran_str(self):
        salt = ''.join(random.sample(string.ascii_letters + string.digits,8))
        return  salt + SALT

class FindPwd(models.Model):
    user = models.OneToOneField(Member,verbose_name='用户',on_delete=models.CASCADE)
    token = models.CharField('email验证token',max_length=32,default=None)
    timestamp = models.DateTimeField(default=timezone.now,verbose_name='令牌创建时间')

    def __str__(self):
        return '%s@%s'%(self.user,self.token)

    def generate_token(self):
        #令牌生成
        year = self.timestamp.year
        month = self.timestamp.month
        day = self.timestamp.day
        date = "%s-%s-%s"%(year,month,day)
        token = hashlib.md5((self.ran_str()+date).encode('utf-8')).hexdigest()
        return token

    def ran_str(self):
        salt = ''.join(random.sample(string.ascii_letters + string.digits,8))
        return  salt + SALT
