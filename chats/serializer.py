from . models import Conversation,Message
from rest_framework import serializers
from django.template.context_processors import request
class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields= '__all__'
        read_only_fields=('user_1','user_2','created_time')



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model= Message
        fields= '__all__'
        read_only_fields=('conversation','sender','created_at','is_read')



class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=Message
        fields = '__all__'
        read_only_fields = ('conversation', 'sender', 'created_at', 'is_read')

    def create(self,validated_data):
        request=self.context.get('request')
        user=request.user
        conversation=self.context.get('conversation')
        if  (validated_data.get('text') or
            validated_data.get('image') or
            validated_data.get('file') or
            validated_data.get('post')) and conversation:
            message=Message.objects.create(
                conversation=conversation,
                sender=user,
                text=validated_data.get('text'),
                image=validated_data.get('image'),
                file=validated_data.get('file'),
                post=validated_data.get('post')
            )
            return message
        raise serializers.ValidationError({'details':'can not send an empty message'})






