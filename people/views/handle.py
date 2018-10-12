from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect,Http404
from people.forms import RegisterForm,LoginForm
from people.models import Member,Follower,EmailVerified as Email,FindPwd
from question.models import Topic,Comment
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.cache import cache
from wen.settings import NUM_TOPIC_PER_PAGE,NUM_COMMENT_PER_PAGE,DEFAULT_FROM_EMAIL
from django.conf import settings
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.core.mail import send_mail
import datetime
from django.contrib.auth import logout as auth_logout,authenticate,login as auth_login
SITE_URL = getattr(settings,'SITE_URL')

@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            new_user = Member.objects.create_user(username=data['username'],email=data['email'],password=data['password'])
            new_user.save()

            email_verified = Email(user=new_user)
            email_verified.token = email_verified.generate_token()
            email_verified.save()

            #此处进行邮箱验证
            try:
                send_mail('欢迎加入问问','%s你好：\r\n请点击链接验证您的邮箱：%s%s'%(new_user.username,SITE_URL,reverse('user:email_verified',args=(new_user.id,email_verified.token))),
                      DEFAULT_FROM_EMAIL,[data['email'],]
                      )
            except:
                messages.error(request,'由于测试期间服务器发送大量邮件，可能qq邮箱暂时禁止本站发送邮件，测试期间未验证邮箱不影响使用')
            messages.success(request,'恭喜注册成功，请到您的邮箱进行邮箱验证。如果没有收到验证邮件，请查阅你的垃圾信箱。')
            user = authenticate(username=data['username'],password=data['password'])
            auth_login(request,user)
            go = reverse('question:index')
            is_auto_login = request.POST.get('auto')
            if not is_auto_login:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60)
            return HttpResponseRedirect(go)
    else:
        form = RegisterForm()
    return render(request,'people/register.html',{'form':form})

@csrf_protect
def login(request):
    if request.user.is_authenticated:
        #判断是否已经登陆
        return HttpResponseRedirect(request.META.get('HTTP_PEFERER','/'))
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            if '@' not in username:
                username = username
            else:
                user = Member.objects.get(email=username)
                username = user.username
            #authenticate()用于验证数据库中是否有对应的账号密码
            user = authenticate(username=username,password=data['password'])
            if user is not None:
                auth_login(request,user)
                go = reverse('question:index')
                is_auto_login = request.POST.get('auto')
                if not is_auto_login:
                    request.session.set_expiry(0)
                return HttpResponseRedirect(go)
            else:
                messages.error(request,'密码不正确')
                return render(request,'people/login.html',locals())

    else:
        form = LoginForm()
    return render(request,'people/login.html',{'form':form})

def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('question:index'))

def au_top(request):
    au_list = cache.get('au_topic')
    if not au_list:
        au_list = Member.objects.all().order_by('-au')[:20]
        cache.set('au_top_list',au_list,60)

    user_count = cache.get('user_count')
    if not user_count:
        user_count = Member.objects.all().count()
        cache.set('use_count',user_count,60)
    return render(request,'people/au_top.html',locals())

def user(request,uid):
    user_from_id = Member.objects.get(pk=uid)
    user_a = request.user

    if user_a.is_authenticated:
        try:
            follower = Follower.objects.filter(user_a=user_a,user_b=user_from_id).first()
        except Follower.DoesNotExist:
            follower = None
        topic_list = Topic.objects.order_by('-created_on').filter(author=user_from_id)[:NUM_TOPIC_PER_PAGE]
        comment_list = Comment.objects.order_by('-created_on').filter(author=user_from_id)[:NUM_COMMENT_PER_PAGE]

    return render(request,'people/user.html',locals())

def user_topics(request,uid):
    this_user = Member.objects.get(pk=uid)
    topic_list = Topic.objects.order_by('-created_on').filter(author=uid)
    paginator = Paginator(topic_list,NUM_TOPIC_PER_PAGE)
    page = request.GET.get('page')

    try:
        topic_list = paginator.page(page)
    except PageNotAnInteger:
        topic_list = paginator.page(1)
    except EmptyPage:
        topic_list = paginator.page(paginator.num_pages)
    return render(request,'people/user_topics.html',locals())

def user_comments(request,uid):
    this_user = Member.objects.get(pk=uid)
    comment_list = Comment.objects.order_by('-created_on').filter(author=uid)
    paginator = Paginator(comment_list,NUM_COMMENT_PER_PAGE)
    page = request.GET.get('page')
    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)
    return render(request,'people/user_comments.html',locals())

@login_required
@csrf_protect
def send_verified_email(request):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('user:settings'))
    user = request.user
    if user.email_verified:
        messages.error(request,'您的邮箱已验证')
        return HttpResponseRedirect(reverse('user:settings'))
    last_email = Email.objects.get(user=user)
    if (timezone.now() - last_email.timestamp).seconds < 60:
        messages.error(request,'一分钟内只能申请一次')
    else:
        try:
            email = Email.objects.get(user=user)
            email.token = email.generate_token()
            email.timestamp = timezone.now()
            email.save()
        except Email.DoesNotExist:
            email = Email(user=user)
            email.token = email.generate_token()
            email.save()
        finally:
            send_mail('欢迎加入问问','%s你好：\r\n请点击链接验证您的邮箱：%s%s'%(user.username,SITE_URL,reverse('user:email_verified',args=(user.id,email.token))),
                      DEFAULT_FROM_EMAIL,[user.email],
                      )
            messages.success(request,'邮件发送成功，请到您的邮箱进行邮箱验证。如果没有收到验证邮件，请查阅你的垃圾信箱。')
    return HttpResponseRedirect(reverse('user:settings'))

def email_verified(request,uid,token):
    try:
        user = Member.objects.get(pk=uid)
        email = Email.objects.get(user=user)
    except (Member.DoesNotExist,Email.DoesNotExist):
        return HttpResponseRedirect(reverse('question:index'))
    else:
        if email.token == token:
            user.email_verified = True
            user.save()
            email.delete()
            messages.success(request,'验证成功')
            if not request.user.is_authenticated:
                auth_login(request,user)
            return HttpResponseRedirect(reverse('question:index'))
        else:
            raise Http404

def find_password(request):
    if request.method == 'GET':
        return render(request,'people/find_password.html')
    email = request.POST['email']#需重新定义表单
    user = None
    try:
        user = Member.objects.get(email=email)
    except Member.DoesNotExist:
        messages.error(request,'未找到用户')
    if user:
        find_pwd = FindPwd.objects.filter(user=user)
        if find_pwd:
            find_pwd = find_pwd.first()
            if (timezone.now - find_pwd.timestamp).seconds < 60:
                messages.error(request,'一分钟内只能找回一次密码')
                return HttpResponseRedirect(reverse('question:index'))
        else:
            find_pwd = FindPwd(user=user)
            find_pwd.timestamp = timezone.now()
            find_pwd.token = find_pwd.generate_token()
        find_pwd.save()
        send_mail('重置密码', '%s你好：\r\n请点击链接重置密码：%s%s' % (
        user.username, SITE_URL, reverse('user:first_reset_password', args=(user.id, find_pwd.token))),
                  DEFAULT_FROM_EMAIL, [user.email],
                  )
        messages.success(request,'密码找回邮件已发送')
    return HttpResponseRedirect(reverse('question:index'))

def first_reset_password(request,uid=None,token=None):
    user = Member.objects.get(pk=uid)
    #如果数据库中没有提供的token的记录，
    # 意味着该用户没有请求修改密码或者用户不存在，
    # 该请求为非法请求，返回主页
    find_pwd = FindPwd.objects.filter(user=user)
    if not find_pwd:
        messages.error(request,'错误')
        return HttpResponseRedirect(reverse('user:find_pass'))
    find_pwd = find_pwd.first()

    if (timezone.now() - find_pwd.timestamp).days < 3:
        if find_pwd.token == token:
            request.session['find_pwd'] = uid
            return render(request,'people/reset_password.html')
        else:
            raise Http404
    else:
        raise Http404

def reset_password(request):
    if request.method == 'GET':
        raise Http404
    #需要一个form
    password = request.POST.get('password','')
    if len(password) < 6:
        messages.error(request,'密码长度不能少于6位')
        return render(request,'people/reset_password.html')
    uid = request.session['find_pwd']
    user = Member.objects.get(pk=uid)
    if user:
        user.set_password(password)
        user.save()
        FindPwd.objects.get(user=user).delete()
        del request.session['find_pwd']
        messages.success(request,'重置成功，请重新登陆')
        return HttpResponseRedirect(reverse('user:login'))
    return HttpResponseRedirect(reverse('question:index'))




