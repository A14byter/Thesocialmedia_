from django.core.serializers import serialize
from django.template.defaulttags import comment
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .serializer import PostSerializr,CommentSerializer,CommentListSerializer,LikeSerializer,UserLikeSerializer,CreatePostSerializer,SavePostSerializer,SavePostListSerializer
from .models import Post , Comment,Like,Save


class PostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,post_id):
        try :
            post = Post.objects.get(id=post_id)
            serializer =PostSerializr(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)

class CreatePostView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer=CreatePostSerializer(data=request.data,
                                        context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def patch(self,request):
        post_id=request.data.get('post_id')
        post=get_object_or_404(Post,id=post_id,user=request.user)

        serializer=CreatePostSerializer(post,
                                        data=request.data,
                                        context={'request':request},
                                        partial=True
                                        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        user=request.user
        post_id=request.data.get('post_id')
        post=Post.objects.filter(id=post_id,user=user).first()
        if post:
            post.delete()
            return Response({'details':
                             'post successfully deleted'})



class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,post_id):

        serializer = CommentSerializer(data=request.data,
                                       context={
                                           'request':request,
                                           'post_id':post_id

                                                })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request,post_id):

        if not post_id:
            return Response({'error': 'post id is required'}, status=status.HTTP_400_BAD_REQUEST)

        comments = Comment.objects.filter(post_id=post_id).select_related('user','post')
        if not comments.exists():
            return Response({'message': 'no comments exist'}, status=status.HTTP_204_NO_CONTENT)

        serializer = CommentListSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def delete(self,request):
        user=request.user
        post_id=request.data.get('post_id')
        comment_id=request.data.get('comment_id')
        comment=get_object_or_404(Comment,id=comment_id,user=user,post_id=post_id)

        comment.delete()
        return Response({'details':'your comment successfully deleted'},status=status.HTTP_202_ACCEPTED)
    def patch(self,request):
        user=request.user
        comment_id=request.data.get('comment_id')
        post_id=request.data.get('post_id')
        comment = get_object_or_404(Comment,id=comment_id,user=user,post_id=post_id)

        serializer=CommentSerializer(comment,
                                     data=request.data,
                                     context={
                                         'request':request,
                                         'post_id':post_id
                                     },
                                     partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'details':'comment edited'},status=status.HTTP_202_ACCEPTED)
        return Response({'details':'please write a valid text'},status=status.HTTP_400_BAD_REQUEST)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,post_id):


        serializer= LikeSerializer(
            data= {'like_post':True},
            context={'request':request,'post_id':post_id}

        )
        if serializer.is_valid():
            obj=serializer.save()
            if obj:
                return Response({'detail':'post liked'})

        return Response({'detail':'error happned'})

    def delete(self,request,post_id):
        post=Post.objects.filter(id=post_id).first()
        user=request.user

        liked=Like.objects.filter(from_user=user,post=post).first()
        if liked:
            liked.delete()
            return Response({'details':'post unliked'})
        return Response({'details':'something went wrong'})

    def get(self,request):
        like_count=0
        post_id =request.query_params.get('post_id')
        post = get_object_or_404(Post,id=post_id)
        like_objects = Like.objects.filter(post=post)
        for i in like_objects:
            like_count+=1
        return Response({'like_count':like_count})

class UserLikeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,post_id):

        post=get_object_or_404(Post,id=post_id)
        like_list = Like.objects.filter(post=post)
        if not like_list.exists():
            return Response({'details': 'no like exist'}, status=status.HTTP_204_NO_CONTENT)
        serializer=UserLikeSerializer(like_list,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class SavePostView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        post_id=request.data.get('post_id')
        serializer=SavePostSerializer(
            data={'save_post':True},
            context={'request':request,'post_id':post_id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'details':'post saved'})
        return Response({'details':'something went wrong'})

    def delete(self,request):
        user=request.user
        post_id=request.data.get('post_id')
        post=get_object_or_404(Post,id=post_id)
        saved_post=Save.objects.filter(user=user,post=post).first()
        if saved_post:
            saved_post.delete()


class SavePostListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user=request.user
        posts=Save.objects.filter(user=user).order_by('saved_date')
        if not posts.exists():
            return Response({'details':'no post has been saved yet'})

        serializer=SavePostListSerializer(posts,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)






