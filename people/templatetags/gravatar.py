from django import template
from django.conf import settings
import urllib.parse,hashlib
from django.contrib.auth import get_user_model
from django.utils import timezone

GRAVATAR_URL_PREFIX = getattr(settings,'GRAVATAR_URL_PREFIX','heep://www.gravatar.com/')
GRAVATAR_DEFAULT_IMAGE = getattr(settings,'GRAVATAR_DEFAULT_IMAGE','')
GRAVATAR_DEFAULT_RATING = getattr(settings,'GRAVATAR_DEFAULT_RATING','g')
GRAVATAR_DEFAULT_SIZE = getattr(settings,'GRAVATAR_DEFAULT_SIZE',48)

User = get_user_model()

register = template.Library()

def _get_user(user):
    if not isinstance(user,User):
        try:
            user = User.object.get(username=user)
        except User.DoesNotExist:
            raise Exception('Bad user for gravatar')
    return user.email

def _get_gravtar_id(email):
    email = email.encode()
    return hashlib.md5(email).hexdigest()

@register.simple_tag
def gravatar(user,size=None):
    try:
        if isinstance(user,User):#传进用户名
            return gravatar_url_for_user(user,size)
        return gravatar_url_for_email(user, size)#传进用户邮箱
    except ValueError:
        raise template.TemplateSyntaxError('语法错误')

@register.simple_tag
def gravatar_url_for_user(user,size=None):
    if user.avatar and user.avatar !='':#已有头像
        img = 'http://pdln1hvzf.bkt.clouddn.com/' + user.avatar + '?v={}'.format(timezone.now().timestamp())
        return img
    else:
        email = _get_user(user)
        return gravatar_url_for_email(email,size)
@register.simple_tag
def gravatar_url_for_email(email,size=None):
    gravatar_url = '%savatar/%s'%(GRAVATAR_URL_PREFIX,_get_gravtar_id(email))

    parameters = [p for p in (('d',GRAVATAR_DEFAULT_IMAGE),('s',GRAVATAR_DEFAULT_SIZE or size),('r',GRAVATAR_DEFAULT_RATING))if p[1]]
    if parameters:
        gravatar_url += '?' + urllib.parse.urlencode(parameters,doseq=True)#将参数按照url格式拼接到url上，详自行查询文档
    return gravatar_url

