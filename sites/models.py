from django.db import models

# 友站模块的models
class Category(models.Model):
    name = models.CharField(max_length=100,verbose_name='类别名称')
    def __str__(self):
        return self.name

class CoolSite(models.Model):
    category = models.ForeignKey(Category,verbose_name='所属类别',on_delete=models.CASCADE)
    url = models.URLField(verbose_name='站点地址')
    name = models.CharField(max_length=100,verbose_name='站点名称')
    description = models.TextField(blank=True,verbose_name='站点介绍')
    created_on = models.DateTimeField(auto_now_add=True,verbose_name='添加时间')

    def __str__(self):
        return self.name