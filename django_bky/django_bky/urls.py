"""django_bky URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path

from app01 import views
from django.views.static import serve
from django_bky import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    #注册
    path('register/',views.register),
    # 登录
    path('login/', views.login),
    #验证码
    path('get_code/',views.get_code),
    # 首页
    path('home/', views.home),
    #修改密码
    path('set_password/',views.set_password),
    #退出登录
    path('logout/',views.logout),

    #点赞点踩
    path('up_or_down/',views.up_or_down),
    #评论
    path('comment/',views.comment),


    #暴露后端指定的文件夹路径
    re_path('^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),

    #文章详情页  127.0.0.1/zhangsan/article/123
    re_path('(?P<username>\w+)/article/(?P<article_id>\d+)',views.article_detail),

    #左侧菜单栏的功能
    # #分类
    # re_path('(?P<username>\w+)/category/(\d+)',views.site),
    # #标签
    # re_path('(?P<username>\w+)/tag/(\d+)',views.site),
    # #日期
    # re_path('(?P<username>\w+)/archive/(\d+)',views.site),
    #可以合成一个
    re_path('(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/',views.site),

    #个人站点 \w 可以匹配任何字符 a-z A-z 0-9 _
    re_path('(?P<username>\w+)/',views.site),






]
