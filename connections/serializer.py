from django.contrib.auth import get_user_model
from django.template.context_processors import request

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate

from .models import Notification,FeedBlock
from posts.models import Post
from django.contrib.auth.models import User



class NotifSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source="from_user.username" ,read_only=True)
    avatar=serializers.SerializerMethodField()


    class Meta:
        model= Notification
        fields = ('id','username','avatar','text','type','time')


    def get_avatar(self, obj):
        if hasattr(obj.from_user, "page") and obj.from_user.page.avatar:
            return obj.from_user.page.avatar.url
        return None

class FeedSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    avatar = serializers.SerializerMethodField()
    class Meta:
        model=Post
        fields=('username','avatar','head','caption','file','created_date')
    def get_avatar(self,obj):
        if hasattr(obj.user,"page") and obj.user.page.avatar:
            return obj.user.page.avatar.url
        return None
class FeedBlockSerializer(serializers.ModelSerializer):
    feed_block=serializers.BooleanField(default=False)
    class Meta:
        model=Post
        fields=('feed_block')
    def create(self,validated_data):
        user=request.user
        target_user=self.context.get('target_user')
        if validated_data['feed_block']:
            feed_block,created= FeedBlock.objects_get_or_create(
                user=user,
                target_user=target_user
            )
            return feed_block


class SearchUserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    class Meta:
        model=User
        fields=('username','first_name','last_name','avatar')
    def get_avatar(self,obj):
        if hasattr(obj,"page") and obj.page.avatar:
            return obj.page.avatar.url
        return None
        
class ExploreSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields=('user','head','caption','file','type')



