from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

class Notification(models.Model):
    FOLLOW =1
    REQUEST_FOLLOW=2
    ACCEPT_FOLLOW=3
    LIKE=4
    COMMENT=5
    NOTIFICATION_TYPE_CHOICES =(
        (FOLLOW,'follow'),
        (REQUEST_FOLLOW,'request_follow'),
        (ACCEPT_FOLLOW,'acception_follow'),
        (LIKE,'like'),
        (COMMENT,'comment')
    )

    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_notif')
    to_user= models.ForeignKey(User,on_delete=models.CASCADE,related_name='received_notif')
    type = models.PositiveSmallIntegerField(choices=NOTIFICATION_TYPE_CHOICES,default=FOLLOW)
    time=models.DateTimeField(auto_now_add=True)
    text=models.CharField(max_length=120,blank=True)

class FeedBlock(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='blocker_user')
    target_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='blocked_user')

class ExploreType(models.Model):
        NEWS=1
        PUBLIC=2
        SHOPING=3
        VLOG=4
        EDUCATIONAL=5
        EXPLORE_TYPE_CHOICES= (
            (NEWS,'news'),
            (PUBLIC,'public'),
            (SHOPING,'shoping'),
            (VLOG,'vlog'),
            (EDUCATIONAL,'educatinal')
        )
        user=models.ForeignKey(User,on_delete=models.CASCADE)
        type= models.PositiveSmallIntegerField(choices=EXPLORE_TYPE_CHOICES,default=PUBLIC)



