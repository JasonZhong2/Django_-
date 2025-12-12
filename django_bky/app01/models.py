from django.db import models


from django.contrib.auth.models import AbstractUser


#用户表
class UserInfo(AbstractUser):
    #手机号
    phone = models.BigIntegerField(verbose_name='手机号',null=True)
    #头像 default：默认 upload_to 上传文件的目录
    avatar = models.FileField(upload_to='avatar/',verbose_name='头像',default='avatar/default.png')


#个人站点表
class Blog(models.Model):
    site_name = models.CharField(max_length=32,verbose_name='站点名称')
    site_title = models.CharField(max_length=64,verbose_name='站点标题')
    # 存放css/js文件的路径
    site_theme = models.CharField(max_length=32,verbose_name='站点样式')

    #用户和个人站点是一对一
    user = models.OneToOneField(to='UserInfo',on_delete=models.CASCADE)

    def __str__(self):
        return self.site_name

#文章分类
class Category(models.Model):

    name = models.CharField(max_length=32,verbose_name='文章分类')

    #文章分类和个人站点是一对多的关系
    blog = models.ForeignKey(to='Blog',on_delete=models.CASCADE)

    def __str__(self):
        return self.name


#文章标签
class Tag(models.Model):
    name = models.CharField(max_length=32,verbose_name='文章标签')

    # 文章标签和个人站点是一对多的关系
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

#文章表
class Article(models.Model):
    title = models.CharField(max_length=64,verbose_name='文章标题')
    desc  = models.CharField(max_length=64, verbose_name='文章简介')
    content =models.TextField(verbose_name='文章内容')
    create_time = models.DateField(auto_now_add=False,verbose_name='创建时间')
    up_num = models.IntegerField(verbose_name='点赞数',default=0)
    down_num = models.IntegerField(verbose_name='点踩数',default=0)
    comment_num =models.IntegerField(verbose_name='评论数',default=0)

    #文章表和个人站点是一对多关系
    blog = models.ForeignKey(to='Blog', on_delete=models.CASCADE)
    #文章和分类是 一对多的关系
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE)
    #文章和标签是多对多
    tags=models.ManyToManyField(to='Tag')

    def __str__(self):
        return self.title


#点赞点踩表
class UpOrDown(models.Model):
    user = models.ForeignKey(to='UserInfo',on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article',on_delete=models.CASCADE)
    is_up = models.BooleanField()  #布尔类型值 传入 0 1

#评论表
class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    content = models.CharField(max_length=255,verbose_name='评论内容')
    #自关联  null=True 不是所有的评论都有子评论 所以可以为空
    patent = models.ForeignKey(to='self',on_delete=models.CASCADE,null=True)