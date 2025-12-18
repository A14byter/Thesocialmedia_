from django.contrib.auth import user_login_failed
from django.shortcuts import render
from pyexpat.errors import messages

from rest_framework.permissions import IsAuthenticated

from .models import Conversation,Message
from .serializer import ConversationSerializer,MessageSerializer,CreateMessageSerializer

from rest_framework.views import APIView,Response
from rest_framework import response,status


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User

from django.conf import settings


class ConversationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        first_user=request.user
        user_name=request.data.get('user_name')
        second_user=User.objects.filter(username=user_name).first()
        if not second_user:
            return Response('could not create a new chat, enter a valid id', status=status.HTTP_400_BAD_REQUEST)
        if first_user.id==second_user.id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_a=first_user
        user_b=second_user
        if user_a.id > user_b.id:
            user_a,user_b=user_b,user_a
        conversation ,created= Conversation.objects.get_or_create(
            user_1=user_a,
            user_2=user_b
        )
        serializer=ConversationSerializer(conversation)

        return Response(serializer.data,status=status.HTTP_201_CREATED)



    def get(self,request):
        first_user=request.user
        conversation_1 = Conversation.objects.filter(user_1=first_user)
        conversation_2 = Conversation.objects.filter(user_2=first_user)
        conversations = list(conversation_1) + list(conversation_2)
        if conversations:
            serializer=ConversationSerializer(conversations,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response('you have no any chat yet!',status=status.HTTP_404_NOT_FOUND)

    def delete(self,request):
        user=request.user
        conv_id=request.data.get('conversation_id')
        conv=Conversation.objects.filter(id=conv_id).first()
        if not conv:
            return Response({'context':'does not existd'},status=400)
        if not user in[conv.user_1,conv.user_2]:
            return Response({'context':'failed'},status=400)
        conv.delete()
        return Response({'context':'deleted'},status=200)



class MessageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user=request.user
        conversation_id=request.data.get('conversation_id')
        conv=Conversation.objects.filter(id=conversation_id).first()
        if not conv:
            return Response({'context':'does not exists'},status=400)
        user_a=conv.user_1
        user_b=conv.user_2
        if user.id==user_a.id or user.id == user_b.id :
            serializer = CreateMessageSerializer(data=request.data,
                                                 context={'request':request,
                                                          'conversation':conv},
                                                 partial=True)
            if serializer.is_valid():
                message=serializer.save()


                layer = get_channel_layer()
                async_to_sync(layer.group_send)(
                    f"chat_{conv.id}",
                    {
                        "type": "chat_message",
                        "sender": user.id,
                        "text": message.text,
                        "image": message.image.url if message.image else None,
                        "file": message.file.url if message.file else None,
                        "post" : message.post if message.post else None

                    }
                )

                return Response(serializer.data, status=201)

            return Response({'context':'please input valid data'},status=400)
        return Response({'context':'you have not started this chat'},status=400)

    def get(self,request):
        user=request.user
        conversation_id=request.query_params.get('conversation_id')
        conv=Conversation.objects.filter(id=conversation_id).first()
        if not conv:
            return Response({'context':'this conversation does not exist'},status=400)


        if user not in [conv.user_1, conv.user_2]:
            return Response({'error': 'access denied'}, status=403)

        if user == conv.user_1:
            first_user = conv.user_1
            second_user = conv.user_2

        else:
            first_user = conv.user_2
            second_user = conv.user_1

        sent_messages=Message.objects.filter(conversation=conv,sender=first_user)
        received_messages=Message.objects.filter(conversation=conv,sender=second_user)
        serializer_1=MessageSerializer(sent_messages,many=True)
        serializer_2=MessageSerializer(received_messages,many=True)

        if sent_messages.exists() or received_messages.exists():
            data = {
                'sent_messages':serializer_1.data,
                'received_messages':serializer_2.data
            }
            received_messages.update(is_read=True)
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f"chat_{conv.id}",
                {
                    "type": "read_event",
                    "reader": user.id
                }
            )
            return Response(data,status=200)
        return Response({
            'received_messages': [],
            'sent_messages': [],
            'context': 'no message here yet'
        }, status=200)

    def delete(self,request):
        user = request.user
        conv_id = request.data.get('conversation_id')
        conv = Conversation.objects.filter(id=conv_id).first()
        if not conv:
            return Response({'context': 'failed'}, status=400)
        message_id = request.data.get('message_id')
        message = Message.objects.filter(id=message_id).first()
        if not message:
            return Response({'context': 'failed'}, status=400)


        if not user in [conv.user_1, conv.user_2]:
            return Response({'context': 'failed'}, status=404)
        if user == conv.user_1:
            first_user = conv.user_1
            second_user = conv.user_2
        else:
            first_user = conv.user_2
            second_user = conv.user_1

        if message.sender != first_user or message.conversation != conv:
            return Response({'context': 'not validated'}, status=403)

        message.delete()
        return Response({'context':'message has been deleted'})



class LikeMessageView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user=request.user
        conv_id=request.data.get('conversation_id')
        conv=Conversation.objects.filter(id=conv_id).first()
        if not conv:
            return Response({'context':'failed'},status=400)
        message_id=request.data.get('message_id')
        message=Message.objects.filter(id=message_id).first()
        if not message:
            return Response({'context': 'failed'}, status=400)

        like = request.data.get('like_message')
        if isinstance(like, str):
            like = like.lower() == 'true'

        if not user in [conv.user_1, conv.user_2]:
            return Response({'context':'failed'},status=404)
        if user==conv.user_1:
            first_user=conv.user_1
            second_user=conv.user_2
        else:
            first_user=conv.user_2
            second_user=conv.user_1

        if message.sender != second_user or message.conversation != conv:
            return Response({'context': 'not validated'}, status=403)

        if  like is True and message.is_liked==False:
            message.is_liked=True
            message.save()
            return Response({'context':'liked'},status=200)
        elif  like is False and message.is_liked==True:
            message.is_liked=False
            message.save()
            layer = get_channel_layer()
            async_to_sync(layer.group_send)(
                f"chat_{conv.id}",
                {
                    "type": "like_event",
                    "message_id": message.id,
                    "liked": message.is_liked,
                }
            )
            return Response({'context':'unliked'},status=200)
        else:
            return Response({'context':'not validated'})





























