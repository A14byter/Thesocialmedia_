from django.db import models
from django.contrib.auth.models import User

from connections.models import ExploreType


class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='post_user')
    head = models.CharField(max_length=20,blank=True,null=True)
    caption = models.CharField(max_length=400, blank=True,null=True)
    file =models.FileField(blank=True , null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    is_enable = models.BooleanField(default=True)
    type = models.PositiveSmallIntegerField(choices=ExploreType.EXPLORE_TYPE_CHOICES,default=1)


class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='comment_user')
    post =models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comment_post')
    comment = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(User,blank=True,related_name='comment_like')

class Like(models.Model):
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='like_user')
    post = models.ForeignKey(Post,on_delete=models.CASCADE,null=True,blank=True,related_name='like_post')
    
class Save(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='save_user')
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='save_post')
    saved_date=models.DateTimeField(auto_now_add=True)




