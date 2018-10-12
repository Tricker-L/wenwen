from django import forms
from question.models import Topic,Comment

class TopicForm(forms.ModelForm):
    title = forms.CharField(label='标题',required=True)
    content = forms.CharField(label='内容',required=False)

    def clean_titil(self):
        title = self.cleaned_data.get('title').strip()
        if len(title) < 3:
            raise forms.ValidationError('标题太短了')
        elif len(title) > 100:
            raise forms.ValidationError('标题太长了')
        else:
            return  title
    def clean_content(self):
        content = self.cleaned_data.get('content').strip()
        if len(content) > 5000:
            raise forms.ValidationError('文章内容不可超过5000字')
        else:
            return content
    class Meta:
        model = Topic
        fields = ('title','content')

class ReplyForm(forms.ModelForm):
    content = forms.CharField(label='内容',required=False)

    def clean_content(self):
        content = self.cleaned_data.get('content').strip()#顺便去掉空格
        if len(content) > 800:
            raise forms.ValidationError('评论内容过长')
        elif len(content) == 0:
            raise forms.ValidationError('评论内容不能为空')
        else:
            return content
    class Meta:
        model = Comment
        fields = ('content',)