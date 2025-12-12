
from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth
from app01 import models

#注册自定义标签
register = template.Library()

@register.inclusion_tag('left_menu.html')
def left(username):

    user_obj = models.UserInfo.objects.filter(username=username).first()

    blog = user_obj.blog


    # 查询该用户的每个分类的文章数
    category_list = models.Category.objects.filter(blog=blog). \
        annotate(count_num=Count('article__pk')). \
        values_list('name', 'count_num', 'pk')

    # 查询该用户的标签数
    tag_list = models.Tag.objects.filter(blog=blog). \
        annotate(count_num=Count('article__pk')). \
        values_list('name', 'count_num', 'pk')

    # 查询该用户的日期归档
    # 1 查询该用户所写的所有的文章
    # 2 按照年月进行分组, 查询月份
    # 3 按照月份进行分组 查询每个月的文章数
    date_list = models.Article.objects.filter(blog=blog) \
        .annotate(mouth=TruncMonth('create_time')).values('mouth') \
        .annotate(count_num=Count('pk')) \
        .values_list('mouth', 'count_num')

    return locals()