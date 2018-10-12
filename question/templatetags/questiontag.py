from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from question.models import Notice,FavoritedTopic
from people.models import Member as User
from people.models import Follower
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
import misaka
import re
import datetime
from django.utils import timezone

register = template.Library()

@register.simple_tag
def notice_set_all_readed(user):
    Notice.objects.filter(to_user=user,is_read=False,is_deleted=False).update(is_read=True)
    return ''

@register.simple_tag
def get_fav_count(user):
    num = FavoritedTopic.objects.filter(user=user).count()
    return num
#@register.assignment_tag从django2.0后已经被移除
@register.simple_tag
def num_notice(user):
    num = Notice.objects.filter(to_user=user,is_read=False,is_deleted=False).count()
    return num

@register.simple_tag
def get_following_count(user):
    num = Follower.objects.filter(user_a=user).count()
    return num

@register.simple_tag
def page_item_idx(page_obj,p,forloop):
    return page_obj.page(p).start_index()+forloop['counter0']

@register.filter
def time_to_now(value):
    now = timezone.now()
    delta = now - value
    if delta.days > 365:
        return '%s年前'%str(delta.days//365)
    if delta.days > 30:
        return '%s月前'%str(delta.days//30)
    if delta.days > 0:
        return '%s天前'%str(delta.days)
    if delta.seconds > 3600:
        return '%s小时前'%str(delta.seconds//3600)
    if delta.seconds > 60:
        return  '%s分钟前'%str(delta.seconds//60)
    return '刚刚'
@register.filter(is_safe=True)
def topic_title_cut(title,num):
    num = int(num)
    if len(title) > num:
        title = title[:num]+'...'
        return title
    else:
        return title

class BaseRenderer(misaka.HtmlRenderer):
    def autolink(self,link,is_email):
        if is_email:#邮箱链接
            return '<a href="mailto:%(link)s">%(link)s</a>'%{'link':link}
        content = link.replace('http://','').replace('https://','')#其他链接
        return '<a href="%s"target="_blank">%s</a>'%(link,content)

class CommentRenderer(BaseRenderer):
    def header(self,text,level):
        if level < 4:
            return '<p>#%s</p>'%text
        return '<h%d>%s</h%d>'%(level,text,level)

class TopicRenderer(BaseRenderer):
    pass

@register.filter(is_safe=True)
@stringfilter
def my_markdown(value,flag):
    extensions = (
        misaka.EXT_NO_INTRA_EMPHASIS | misaka.EXT_FENCED_CODE | misaka.EXT_AUTOLINK |
        misaka.EXT_TABLES | misaka.EXT_STRIKETHROUGH | misaka.EXT_SUPERSCRIPT
    )
    if flag == 'comment':
        renderer = CommentRenderer(flags=misaka.HTML_ESCAPE | misaka.HTML_HARD_WRAP)
    else:
        renderer = TopicRenderer(flags=misaka.HTML_ESCAPE | misaka.HTML_HARD_WRAP)
    md = misaka.Markdown(renderer,extensions=extensions)
    md = md(force_text(value))
    return mark_safe(md)


