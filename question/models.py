from django.db import models
from people.models import Member as User
from django.db.models.signals import post_save
from django.utils import timezone
# Create your models here.

class Category(models.Model):
    #类别表
    name = models.CharField(max_length=100,verbose_name='类别名称')
    def __str__(self):
        return self.name

class Node(models.Model):
    #节点表
    name = models.CharField(max_length=100,verbose_name='节点名称')
    slug = models.SlugField(max_length=100,verbose_name='url标识符')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_on = models.DateTimeField(blank=True,null=True,auto_now=True,verbose_name='更新时间')
    num_topics = models.IntegerField(default=0,verbose_name='主题数')
    category = models.ForeignKey(Category,verbose_name='所属类别',on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Topic(models.Model):
    #主题表
    title = models.CharField(max_length=100,verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    node = models.ForeignKey(Node,verbose_name='所属节点',on_delete=True)
    author = models.ForeignKey(User,verbose_name='作者',on_delete=models.CASCADE)
    num_views = models.IntegerField(default=0,verbose_name='浏览量')
    num_comments = models.IntegerField(default=0,verbose_name='评论数')
    last_reply = models.ForeignKey(User,related_name='+',verbose_name='最后回复者',on_delete=True)#关闭反向查询
    created_on = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_on = models.DateTimeField(blank=True, null=True, auto_now=True, verbose_name='更新时间')
    def __str__(self):
        return self.title
    def views_add(self):
        self.num_views += 1
        self.save()
    def num_comments_add(self):
        self.num_comments += 1
        #self.save()
    def updated_on_now(self):
        self.updated_on = timezone.now()
    def last_reply_update(self,member):
        self.last_reply = member

class Comment(models.Model):
    #评论内容表
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, verbose_name='作者',on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic,verbose_name='所属主题',on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    def __str__(self):
        return self.content

class Notice(models.Model):
    #用户通知表
    from_user = models.ForeignKey(User,related_name='+',verbose_name='来自用户',on_delete=models.CASCADE)
    to_user = models.ForeignKey(User,related_name='+',verbose_name='接收用户',on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic,null=True,verbose_name='主题',on_delete=models.CASCADE)
    content = models.TextField(verbose_name='内容')
    time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    def __str__(self):
        return self.content

class FavoritedTopic(models.Model):
    user = models.ForeignKey(User, verbose_name='用户',on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic,verbose_name='主题',on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id)

def create_notice(sender,**kwargs):
    #评论产生时需要对其进行判断，如非题主发表的评论，则需要向题主发送通知
    #因此可以用django.db.models.signals.post_save来进行这一操作
    #post_save是表在进行存储时，调用save会自动调用post_save信号
    #通过post_save内置函数connect()可以关联一些函数，在进行存储操作之前先执行一些操作,因此无需在视图函数中完成
    comment = kwargs['instance']#捕捉评论的内容
    if comment.author != comment.topic.author:
        Notice.objects.create(from_user=comment.author,to_user=comment.topic.author,topic=comment.topic,content=comment.content)


#关联Comment表，在其进行存储前先执行create_notice
post_save.connect(create_notice,sender=Comment)
