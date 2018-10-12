from django.contrib import admin
from django import forms
# Register your models here.
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from people.models import Member,Follower

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='密码',widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码',widget=forms.PasswordInput)
    class Meta:
        model = Member
        fields = ('email','username')
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1!=password2:
            raise forms.ValidationError('两次输入验证失败')
        return password2
    def save(self,commit=True):
        user = super(UserCreationForm,self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()
    class Meta:
        model = Member
        fields = ('email','username','password','is_active','is_admin',)
    def clean_password(self):
        return self.initial['password']#返回原始数据

class MyUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id','email','username','email_verified','last_login','is_active',)
    list_display_links = ('id','email','username')
    list_filter = ('email','email_verified',)
    #将字段按块展示
    fieldsets = (
        (None,{'fields':('username','email',
                        'date_joined','password',
                        'is_active','is_admin',
                        'avatar')
               }
         ),
        ('状态',{'fields':('email_verified','last_ip',
                         'au','topic_num','comment_num')
               }
         ),
        ('社交网络',{'fields':('weibo_id','blog')
                 }
         ),
    )
    #创建新记录时需要填写的数据
    add_fieldsets = (
        (None,{
            'classes':('wide',),
            'fields':('email','username','password1','password2','is_active','is_admin')
        }
         ),
    )
    search_fields = ('id','email','username')#可供搜索的字段
    ordering = ('id','email','email_verified')
    filter_horizontal = ()#设置与groups关联的多选框
admin.site.register(Member,MyUserAdmin)
admin.site.register(Follower)

