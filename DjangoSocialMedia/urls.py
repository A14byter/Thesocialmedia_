from unittest.mock import patch

from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import RegisterView ,ProfileView,MyPageView,PageView,FollowView,GetRequestView,FollowerView,FollowingView
from posts.views import PostView,CreatePostView,CommentView,UserLikeView,SavePostView,SavePostListView,LikeView
from connections.views import FeedView,NotifListView,ExploreView,SearchUserView
from chats.views import ConversationView,MessageView,LikeMessageView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', RegisterView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/',ProfileView.as_view()),


    path('homepage/',MyPageView.as_view(),name='home_page_url'),
    path('homepage/followers/',FollowerView.as_view(),name='followers'),
    path('homepage/followings/',FollowingView.as_view()),
    path('homepage/add-post/',CreatePostView.as_view()),
    path('homepage/posts/<int:post_id>/',PostView.as_view()),
    path('homepage/posts/<int:post_id>/comments/',CommentView.as_view()),
    path('homepage/posts/<int:post_id>/like/',LikeView.as_view()),
    path('homepage/posts/<int:post_id>/likes/',UserLikeView.as_view()),

    path('saved-posts/',SavePostListView.as_view(),name='saved_posts_lists'),
    path('save_post/',SavePostView.as_view(),name='save_post'),

    path('feed/',FeedView.as_view(),name='feed'),
    path('feed/<int:post_id>/',PostView.as_view()),
    path('feed/<int:post_id>/comments/',CommentView.as_view()),
    path('feed/<int:user_id>/',PageView.as_view()),

    path('explore/',ExploreView.as_view()),
    path('explore/<int:post_id>/',PostView.as_view()),
    path('explore/<int:post_id>/comments/',CommentView.as_view()),
    path('explore/<int:post_id>/<int:page_id>/',PageView.as_view()),

    path('follow/',FollowView.as_view()),

    path('Notifications/',NotifListView.as_view()),
    path('search_user/',SearchUserView.as_view()),
    path('user_page/',PageView.as_view()),
    path('user_page/followers/',FollowerView.as_view()),
    path('user_page/followings/',FollowingView.as_view()),

    path('conversations/',ConversationView.as_view()),
    path('conversations/messages/',MessageView.as_view()),
    path('conversations/<int:conversation_id>/<int:message_id>/',LikeMessageView.as_view())






]
