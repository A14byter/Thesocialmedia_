from gc import get_objects
from django.shortcuts import render
from django.core.serializers import serialize
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.shortcuts import get_object_or_404
from .serializer import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Location,Profile,Device ,Page,RequestUser,Follow
from posts.models import Post,Comment
from rest_framework import status
from .serializer import RegisterSerializer ,ProfileSerializer ,FollowSerializer ,PageSerializer,RequestUserSerializer
from posts.serializer import PostSerializr,CommentSerializer
from connections.models import Notification

from rest_framework.permissions import IsAuthenticated
User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        profile = request.user.profile
        serializer =ProfileSerializer(profile)
        return Response(serializer.data)


    def patch(self,request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile,data=request.data ,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data ,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class FollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        from_user = request.user
        to_user_name =request.data.get('to_user_name')
        to_user = get_object_or_404(User, username=to_user_name)
        target_page= get_object_or_404(Page,user_name=to_user)

        if from_user==to_user:
            return Response({'context': "can't follow yourself"},status=400)

        if  not target_page.is_private:
            serializer = FollowSerializer(
                data={'follow':True},
                context ={'request':request,'following':to_user}

            )
            if serializer.is_valid():
                result = serializer.save()
                if result is None:
                    return Response({'details' :'something went wrong'})
                return Response({'details':'followed'})
            return Response({'details':'bad request'},status=status.HTTP_400_BAD_REQUEST)

        elif target_page.is_private:
            serializer= RequestUserSerializer(
                data={'follow_request':True},
                context={'request':request,'to_user':to_user}
            )
            if serializer.is_valid():
                result=serializer.save()
                if result is None:
                    return Response({'details':'something went wrong'})
                return Response({'details':'request sent'})
            return Response({'details':'bad request'}, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request):
        user=request.user
        target_username=request.data.get('target_username')
        target_user=get_object_or_404(User,username=target_username)
        follow_request=RequestUser.objects.filter(from_user=user,to_user=target_user,is_accepted=False).first()
        if follow_request:
            follow_request.delete()
            return Response({'context':'request has ben canceled'})
        return Response({'context': 'something went wrong'})




class GetRequestView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user
        from_user_username =request.data.get('from_username')
        from_user = get_object_or_404(User,username=from_user_username)
        request_user = RequestUser.objects.filter(to_user= user,from_user=from_user).first()
        if  request_user is None:
            return Response({'details': 'follow request not found'}, status=404)

        is_accepted = request.data.get('is_accepted','false').lower()== 'true'
        if is_accepted :
            request_user.is_accepted=True
            request_user.save()

            serializer_follow= FollowSerializer(
                data={'follow':True},
                context={'request':request,'follower':from_user,'following':user}
                )


            if serializer_follow.is_valid():
                serializer_follow.save()
                request_user.delete()
                return Response({'details':'request accepted'})
            else:
                return Response(serializer_follow.errors, status=400)


        else :
            request_user.delete()
            return Response({'details':'request rejected'})






class FollowerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        k=0
        username = request.query_params.get('username','')
        follow = Follow.objects.filter(following__username=username)
        if not follow.exists():
            return Response({'details':'no follower exists'})
        follower_user=[f.follower for f in follow]
        page=Page.objects.filter(user_name__in=follower_user)

        for i in follow:
            k+=1

        serializer = PageSerializer(page ,many=True)
        return Response({"followers" :serializer.data,
                        "count":k})
    def delete(self,request):
        first_user=request.user
        second_username=request.data.get('second_username')
        second_user=get_object_or_404(User,username=second_username)
        follow=Follow.objects.filter(follower=second_user,following=first_user).first()
        if follow:
            follow.delete()
            return Response({'user has been removed'})
        return Response({'context':'something went wrong'})




class FollowingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        k=0
        username = request.query_params.get('username','').strip()

        follow = Follow.objects.filter(follower__username=username)
        if not follow.exists():
            return Response({'details':'no following exists'})

        following_user = [f.following for f in follow]

        page=Page.objects.filter(user_name__in=following_user)
        for i in follow:
            k+=1

        serializer = PageSerializer(page,many=True)
        return Response({"followings" :serializer.data,
        "count": k})

    def delete(self, request):
        first_user = request.user
        second_username = request.data.get('second_username')
        second_user=get_object_or_404(User,username=second_username)
        follow = Follow.objects.filter(follower=first_user, following=second_user).first()
        if follow:
            follow.delete()
            return Response({'context':'user has been unfollowed'})
        return Response({'context': 'something went wrong'})



class MyPageView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        k=0
        f=0
        p=0
        user = request.user
        page = Page.objects.filter(user_name=user).first()
        post = Post.objects.filter(user=user)
        follower = Follow.objects.filter(following=user)
        for i in follower:
            k+=1
        following = Follow.objects.filter(follower=user)
        for h in following:
            f+=1
        for d in post:
            p+=1

        serializer_1 = PageSerializer(page)
        serializer_2 = PostSerializr(post,many=True)
        return Response({'profile' :serializer_1.data,
                         'posts' :serializer_2.data,
                        'followers':k,
                        'following':f,
                        'post':p})


class PageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_param = request.query_params.get('user_param','').strip()
        current_user = request.user

        # بررسی وجود کاربر
        try:
            user_obj = User.objects.get(username=user_param)
        except User.DoesNotExist:
            return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        # داده‌های صفحه و پست‌ها
        page = Page.objects.filter(user_name=user_obj).first()
        posts = Post.objects.filter(user=user_obj)
        followers = Follow.objects.filter(following=user_obj)
        followings = Follow.objects.filter(follower=user_obj)

        serializer_page = PageSerializer(page)
        serializer_posts = PostSerializr(posts, many=True)

        # شرط خصوصی بودن صفحه
        if not page.is_private or Follow.objects.filter(follower=current_user, following=user_obj).exists():
            return Response({
                'profile': serializer_page.data,
                'posts': serializer_posts.data,
                'followers_count': followers.count(),
                'following_count': followings.count(),
                'post_count': posts.count()
            })

        # صفحه خصوصی و کاربر فالو نکرده
        return Response({
            'profile': serializer_page.data,
            'posts': 'page is private',
            'followers_count': followers.count(),
            'following_count': followings.count(),
            'post_count': posts.count()
        })













