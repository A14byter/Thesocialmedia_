from django.contrib.auth import get_user_model
from django.template.context_processors import request

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate

from .models import Profile ,Follow, Page ,RequestUser
from connections.models import Notification

User=get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password_1 = serializers.CharField(required=True,write_only=True)
    password_2 = serializers.CharField(required=True,write_only=True)

    class Meta:
        model=User
        fields =(
            'email' , 'username', 'password_1' , 'password_2', 'first_name', 'last_name'
        )
        extra_kwargs = {
            'first_name' :{'required':False},
            'last_name' :{'required':False},
        }
    def validate(self,attrs):
        if attrs['password_1'] != attrs['password_2']:
            raise serializers.ValidationError({
                'password' :'passwords arent same'
            })
        return attrs

    def create(self,validated_data):
        user= User.objects.create_user(
            username= validated_data['username'],
            email= validated_data['email'],
            first_name=validated_data.get('first_name',''),
            last_name=validated_data.get('last_name',''),
            password=validated_data['password_1'],
        )

        Profile.objects.create(
            user=user

        )
        Page.objects.create(
            user_name=user
        )

        return user

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Profile
        fields = ('user','phone_number','avatar','device','location')

class PageSerializer(serializers.ModelSerializer):
    class Meta :
        model = Page
        fields = '__all__'


class RequestUserSerializer(serializers.ModelSerializer):
    follow_request = serializers.BooleanField(default=False)

    class Meta:
        model = RequestUser
        fields = ('follow_request',)

    def create(self, validated_data):
        request = self.context.get('request')
        from_user = request.user
        to_user = self.context.get('to_user')
        if validated_data['follow_request']:
            follow_request, created = RequestUser.objects.get_or_create(
                from_user=from_user,
                to_user=to_user

            )
            if created:
                Notification.objects.create(
                    from_user=from_user,
                    to_user=to_user,
                    type=Notification.REQUEST_FOLLOW,
                    text=f"{from_user.username} has sent a follow request"
                )
                
            return follow_request
        else:  # پس گرفتن درخواست فالو
            RequestUser.objects.filter(from_user=from_user, to_user=to_user).delete()
            return None


class FollowSerializer(serializers.ModelSerializer):
    follow = serializers.BooleanField(default=False)
    class Meta :
        model =Follow
        fields = ('follow',)
    def create(self,validated_data):
        request = self.context.get('request')
        follower = request.user
        following = self.context.get('following')
        if validated_data['follow'] and (Page.objects.filter(user_name=following,is_private=False).exists() or RequestUser.objects.filter(from_user= follower,to_user=following,is_accepted=True).exists()) :
            follow , created = Follow.objects.get_or_create(
                follower = follower,
                following = following
            )
            if created and not Page.objects.filter(user_name=following,is_private=False).exists():
                Notification.objects.create(
                    from_user=follower,
                    to_user=following,
                    type=Notification.FOLLOW,
                    text=f"{follower.username} started following you."

                )
            else :
                Notification.objects.create(
                    from_user=following,
                    to_user=follower,
                    type=Notification.ACCEPT_FOLLOW,
                    text=f"{following.username} accepted you'r follow request"
                )
            return follow
        else:
            return None


class FollowerSerializer(serializers.ModelSerializer):
    username =serializers.CharField(source="follower.username" , read_only=True)
    avatar = serializers.SerializerMethodField()
    class Meta:
        model = Follow
        fields = ('username','avatar')
    def get_avatar(self, obj):
        if hasattr(obj.follower , "page") and obj.follower.page.avatar:
            return obj.follower.page.avatar.url
        return None

class FollowingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="following.username", read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('username', 'avatar')

    def get_avatar(self, obj):
        if hasattr(obj.following, "page") and obj.following.page.avatar:
            return obj.following.page.avatar.url
        return None


