from django.urls import path,re_path
from question import views
app_name = 'question'

urlpatterns = [
    re_path(r'^$',views.index,name='index'),

    re_path(r'^recent/?$',views.recent,name='recent'),

    re_path(r'^node/([\w-]+)/new/$',views.new,name='new'),
    re_path(r'^node/(?P<node_slug>[\w-]+)',views.node,name='node'),

    re_path(r'^t/(?P<topic_id>\d+)/favtopic/?$', views.fav_topic,name='fav_topic'),
    re_path(r'^t/(?P<topic_id>\d+)/unfavtopic/?$', views.unfav_topic,name='unfav_topic'),
    re_path(r'^topic/(?P<topic_id>\d+)/reply/?$', views.reply, name='reply'),
    re_path(r'^topic/(?P<topic_id>\d+)/edit/?$', views.edit, name='edit'),
    re_path(r'^topic/(?P<topic_id>\d+)/?$',views.topic,name='topic'),

    re_path(r'^notice/(?P<notice_id>\d+)/delete/?$',views.notice_delete,name='notice_delete'),
    path('notice/',views.notice,name='notice'),

]