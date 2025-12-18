from django.core.serializers import serialize
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import request

from .models import Notification,FeedBlock
from accounts.models import Follow
from posts.models import Post
from accounts.models import Page
from .serializer import NotifSerializer,FeedSerializer,FeedBlockSerializer,SearchUserSerializer,ExploreSerializer
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
User = get_user_model()

class NotifListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        to_user=request.user
        notif = Notification.objects.filter(to_user=to_user).order_by('-time')
        serializer= NotifSerializer(notif,many=True,context={'request':request})
        return Response(serializer.data)

class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user=request.user
        following_user=Follow.objects.filter(follower=user).values_list("following",flat=True)
        blocked_user=FeedBlock.objects.filter(user=user).values_list("target_user",flat=True)
        allowed_user=[u for u in following_user if not u in blocked_user]
        if not allowed_user:
            return Response({"detail": "no visible posts"}, status=200)

        post=Post.objects.filter(user__in=allowed_user).order_by('-created_date')
        if not post:
            return Response({'context':'no post here yet'},status=200)
        serializer=FeedSerializer(post,many=True,context={'request':request})
        return Response(serializer.data)


class FeedBlockView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user=request.user
        page_id=request.data.get('post_id')
        page=get_object_or_404(Page,id=page_id)
        target_user=page.user
        serializer=FeedBlockSerializer(data={'feed_block':True},
                                       context={'request':request,
                                                'target_user':target_user})

        if serializer.is_valid():
            serializer.save()
            return Response({'details':'you will not see posts from this user again'})

class SearchUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        query=request.query_params.get('q','').strip()
        if not query:
            return Response({'details':'query must be exist'},status=400)
        user=User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        if not user.exists():
            return Response({'details':'no user found'})
        serializer=SearchUserSerializer(user,many=True)
        return Response(serializer.data)

class ExploreView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        type=request.query_params.get('type')
        post=Post.objects.filter(type=type)
        target_user = Post.objects.filter(type=type).values_list("user",flat=True)
        private_page=Page.objects.filter(is_private=True).values_list("user_name",flat=True)
        allowed_user= [u for u in target_user if not u in private_page]

        allowed_post=Post.objects.filter(user__in=allowed_user,type=type).order_by('-created_date')

        if not allowed_post:
            return Response({'context':'no post here yet.'})

        serializer=ExploreSerializer(allowed_post,many=True)
        return Response(serializer.data)



