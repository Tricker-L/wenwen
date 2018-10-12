from people import views
from django.urls import path,re_path
from question import views as question_views
app_name = 'user'
urlpatterns=[
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),

    re_path(r'^fav_topic/',question_views.fav_topic_list,name='fav_topic'),

    path('users/',views.au_top,name='au_top'),
    re_path(r'user/(?P<uid>\d+)/comments/$', views.user_comments, name='user_comments'),
    re_path(r'user/(?P<uid>\d+)/topics/$', views.user_topics, name='user_topics'),
    re_path(r'user/(?P<uid>\d+)/$',views.user,name='user'),

    re_path(r'^follow/(?P<uid>\d+)/$',views.follow,name='follow'),
    re_path(r'^unfollow/(?P<uid>\d+)/$', views.un_follow, name='unfollow'),
    path('my/following/', views.following, name='following'),

    path('send_verified_email/',views.send_verified_email,name='send_verified_email'),
    re_path(r'^email_verified/(?P<uid>\d+)/(?P<token>\w+)/$',views.email_verified,name='email_verified'),
    path('find_password/',views.find_password,name='find_pass'),
    re_path('^reset_password/(?P<uid>\d+)/(?P<token>\w+)/$',views.first_reset_password,name='first_reset_password'),
    re_path('^reset_password/$',views.reset_password,name='reset_password'),

    path(r'settings/upload_headimage/', views.upload_headimage, name='upload_headimage'),
    path('settings/delete_headimage/', views.delete_headimage, name='delete_headimage'),
    path('settings/',views.profile,name='settings'),
    re_path(r'^password/$',views.password,name='password'),
]