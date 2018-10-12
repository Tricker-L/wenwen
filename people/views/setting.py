from django.http import HttpResponse,HttpResponseRedirect,Http404
from people.forms import ProfileForm,PasswordChangeForm
from people.models import Member,EmailVerified as Email
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout as auth_logout,authenticate,login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render
import base64
import json
from django.conf import settings
from qiniu import Auth
import qiniu.config
from qiniu import BucketManager
from wen.settings import qiniu_AK as AK,qiniu_SK as SK
SITE_URL = getattr(settings,'SITE_URL')

@csrf_protect
@login_required
def profile(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST,instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if user.email != form.old_email:
                user.email_verified = False
                try:
                    email_verified = Email.objects.get(user=user)
                except DoesNotExist:
                    email_verified = Email(user=user)
                email_verified.token = email_verified.generate_token()
                email_verified.save()
            user.save()
            messages.success(request,'设置已更新')
            return render(request,'people/settings.html',{'form':form})
    else:
        form = ProfileForm(instance=user)

    q = Auth(AK,SK)
    buket_name = 'wenwenavatar'
    key_name = 'wenwenavatar/' + user.username
    returnBody = '{"name":$(fname),"key":$(key)}'
    returnUrl = SITE_URL + reverse('user:upload_headimage')
    mimeLimit = 'image/jpeg;image/png;'
    policy = {
        'returnUrl':returnUrl,
        'returnBody':returnBody,
        'mimeLimit':mimeLimit,
        'insertOnly':0,
    }
    uptoken = q.upload_token(buket_name,key_name,3600,policy)
    return render(request,'people/settings.html',{
        'form':form,
        'user':user,
        'uptoken':uptoken,
    })
@csrf_protect
@login_required
def password(request):
    user = request.user
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if user.check_password(data['old_password']):
                #检查用户输入的原密码是否正确
                user.set_password(data['password'])
                user.save()
                messages.success(request,'密码修改成功')
                auth_logout(request)
                user = authenticate(username=user.username, password=data['password'])
                if user is not None:
                    auth_login(request, user)
                return HttpResponseRedirect(reverse('question:index'))
            else:
                messages.error(request,'当前密码输入错误')
                return render(request,'people/password.html',{'form':form})
    else:
        form = PasswordChangeForm()
        return render(request, 'people/password.html', {'form': form})
@csrf_protect
@login_required
def upload_headimage(request):
    user = request.user
    if request.method == 'GET':
        try:
            retstr = request.GET.get('upload_ret')
            retstr = retstr.encode('utf-8')
            dec = base64.urlsafe_b64decode(retstr)
            ret = json.loads(dec)
            if ret and ret['key']:
                request.user.avatar = ret['key']
                request.user.save()
            else:
                raise Http404
            messages.success(request,'头像上传成功')
        except:
            #raise Http404
            messages.error(request,'头像上传失败')
            

    return HttpResponseRedirect(reverse('user:settings'))

@csrf_protect
@login_required
def delete_headimage(request):
    user = request.user

    if user.avatar == None or user.avatar == '':
        messages.error(request,'你还没有上传头像')
    else:
        q = Auth(AK,SK)
        buket = BucketManager(q)
        buket_name = 'wenwenavatar'
        ret,info = buket.delete(buket_name,user.avatar)
        if ret is None:
            messages.error(request,'头像删除失败')
        else:
            user.avatar = ''
            user.save()
            messages.success(request,'头像删除成功')
    return HttpResponseRedirect(reverse('user:settings'))
