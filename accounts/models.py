from django.db import models

from django.conf import settings

from django.contrib.auth.models import User
from posts.models import Post , Comment,Like

class Location(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL , on_delete=models.CASCADE)
    country = models.CharField(max_length=50,blank=True, null=True)
    city = models.CharField(max_length=50,blank=True, null=True)

    class Meta:
        verbose_name = 'location'

class Device(models.Model):
    DEVICE_WEB = 1
    DEVICE_ANDROID = 2
    DEVICE_IOS = 3
    DEVICE_WINDOWS = 4
    DEVICE_MAC = 5
    DEVICE_TYPE_CHOICES =(
        (DEVICE_WEB , 'web'),
        (DEVICE_ANDROID , 'android'),
        (DEVICE_IOS , 'ios'),
        (DEVICE_WINDOWS , 'windows'),
        (DEVICE_MAC , 'mac')
    )
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='devices' ,on_delete=models.CASCADE)
    device_uuid = models.UUIDField('device UUID', null= True)
    last_login = models.DateTimeField('last login' , auto_now=True)
    device_type= models.PositiveSmallIntegerField(choices=DEVICE_TYPE_CHOICES, default=DEVICE_WEB )
    app_version = models.CharField('app version', max_length=20 , null=True , blank = True)
    created_date = models.DateTimeField(auto_now_add=True)




class Profile(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL , on_delete=models.CASCADE, related_name='profile')
    phone_number = models.BigIntegerField(blank=True , null=True, unique=True)
    avatar =models.ImageField(null=True)
    location = models.ForeignKey(to=Location,on_delete=models.CASCADE, null=True, blank=True)
    device = models.ForeignKey(to=Device , on_delete=models.CASCADE,null=True, blank=True)

class Follow(models.Model):
    follower = models.ForeignKey(User,on_delete=models.CASCADE,related_name='followers')
    following = models.ForeignKey(User ,on_delete=models.CASCADE,related_name='followings')
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

class Page(models.Model):
    user_name = models.OneToOneField(to=settings.AUTH_USER_MODEL ,on_delete=models.CASCADE , related_name='user')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    biography = models.CharField(max_length=100 , blank=True , null=True)
    is_private = models.BooleanField(default=False)

class RequestUser(models.Model):
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='follow_request_sent')
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='follow_request_recived')
    date = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together =('from_user' ,'to_user')






