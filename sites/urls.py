from django.urls import path,re_path
from sites import views
app_name = 'sites'

urlpatterns=[
    path('',views.sites,name='sites'),
    path('hot_topic',views.hot_topic,name='hot_topic')

]