from django.db import models
from django.conf import settings
from django.db.models import ManyToManyField

from posts.models import Post
User = settings.AUTH_USER_MODEL

class Conversation(models.Model):
    user_1=models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversation_user_1')
    user_2=models.ForeignKey(User,on_delete=models.CASCADE,related_name='conversation_user_2')
    created_time=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user_1', 'user_2')

    def __str__(self):
        return f"conversation #{self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image=models.ImageField(blank=True,null=True)
    file=models.FileField(blank=True,null=True)
    post=models.ForeignKey(Post,on_delete=models.CASCADE,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_liked=models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} in conv {self.conversation.id}"


