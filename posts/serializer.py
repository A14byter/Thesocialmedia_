from dataclasses import fields

from django.shortcuts import get_object_or_404
from django.template.context_processors import request
from django.template.defaulttags import comment
from rest_framework.response import Response
from rest_framework import status
from .models import Comment,Post,Like,Save
from connections.models import Notification
from accounts.models import Page,Profile
from posts.models import Post


from rest_framework import serializers

class PostSerializr(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields ='__all__'

class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields=('head','caption','file','is_enable','type')
    def create(self,validated_data):
        request=self.context.get('request')
        user=request.user

        if validated_data.get('file'):
            create_post=Post.objects.create(
                user=user,
                head=validated_data.get('head'),
                caption=validated_data.get('caption'),
                file=validated_data.get('file'),
                is_enable=validated_data.get('is_enable'),
                type=validated_data.get('type')

            )
            return create_post
        raise serializers.ValidationError(
            {'details': 'please review the inputs, you must upload a video or picture at least'})

    def update(self, instance, validated_data):
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        return instance



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields =('comment',)
    def create(self, validated_data):
        request=self.context.get('request')
        from_user=request.user
        post_id = self.context.get('post_id')
        post=get_object_or_404(Post,id=post_id)
        comment=validated_data.get('comment','').strip()
        to_user=post.user

        if comment :
            set_comment= Comment.objects.create(
                user=from_user,
                post=post,
                comment=comment
)
            if from_user!=to_user:
                Notification.objects.create(
                    from_user=from_user,
                    to_user=to_user,
                    type=Notification.COMMENT,
                    text=f'{from_user.username} sent a comment:{comment}'
                    )

            return set_comment
        raise serializers.ValidationError({'details': 'Comment text cannot be empty.'})

    def update(self, instance, validated_data):
        instance.comment=validated_data.get('text',instance.comment)
        instance.save()
        return instance

class CommentListSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source='user.username',read_only=True)
    avatar=serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields=('username','avatar','comment')
    def get_avatar(self,obj):
        if hasattr(obj.user,'page') and obj.user.page.avatar:
            return obj.user.page.avatar.url
        return None



class FeedSerializer(serializers.ModelSerializer):
    pass

class LikeSerializer(serializers.ModelSerializer):
    like_post=serializers.BooleanField(default=False)
    class Meta:
        model=Like
        fields =('like_post',)
    def create(self, validated_data):
        request=self.context.get('request')
        from_user= request.user
        post_id= self.context.get('post_id')
        post=get_object_or_404(Post,id=post_id)
        to_user=post.user

        if validated_data['like_post']:
            like , created = Like.objects.get_or_create(
                from_user=from_user,
                post=post
            )
            if created :
                Notification.objects.create(
                    from_user=from_user,
                    to_user=to_user,
                    type=Notification.LIKE,
                    text=f"{from_user.username} has been liked your post."

                )

            return like

        else:

            return None

class UserLikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='from_user.username' , read_only=True)
    avatar = serializers.SerializerMethodField()
    class Meta:
        model = Like
        fields =('username','avatar')
    def get_avatar(self,obj):
        if hasattr(obj.from_user ,"page") and obj.from_user.page.avatar:
            return obj.from_user.page.avatar.url
        return None

class SavePostSerializer(serializers.ModelSerializer):
    save_post=serializers.BooleanField(default=False)
    class Meta:
        model=Save
        fields=('save_post',)
    def create(self, validated_data):
        request=self.context.get('request')
        user=request.user
        post_id=self.context.get('post_id')
        post=get_object_or_404(Post,id=post_id)
        if validated_data['save_post']:
            save_post,created=Save.objects.get_or_create(
                user=user,
                post=post
            )
            return save_post
        else:

            return None

class SavePostListSerializer(serializers.ModelSerializer):
    head=serializers.CharField(source='post.head',read_only=True)
    username=serializers.CharField(source='user.username',read_only=True)
    avatar=serializers.SerializerMethodField()
    caption=serializers.CharField(source='post.caption',read_only=True)
    file=serializers.CharField(source='post.file',read_only=True)
    type=serializers.CharField(source='post.type',read_only=True)
    created_date = serializers.CharField(source='post.created_date', read_only=True)
    class Meta:
        model=Save
        fields=('post','saved_date','avatar','username','head','caption','file','type','created_date')
    def get_avatar(self,obj):
        if hasattr(obj.post.user,"page") and obj.post.user.avatar:
            return obj.post.user.avatar.url
        return None


