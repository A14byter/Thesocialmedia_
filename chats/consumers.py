
import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.conv_id = self.scope['url_route']['kwargs']['conv_id']
        self.room_group_name = f"chat_{self.conv_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data=None, bytes_data=None):
        """
        هندل کردن رویدادهای:
        - text message
        - image upload
        - file upload
        - post share
        - is_read
        - is_liked
        """

        data = json.loads(text_data)
        event_type = data.get("event")

        # -------------------------
        # ارسال پیام (text/image/file)
        # -------------------------
        if event_type == "message":
            sender = data.get("sender")
            text = data.get("text", "")
            image_data = data.get("image")
            file_data = data.get("file")
            post = data.get("post")

            image_url = None
            file_url = None

            # ذخیره عکس در media
            if image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                file_name = default_storage.save(
                    f"chats/images/msg.{ext}",
                    ContentFile(base64.b64decode(imgstr))
                )
                image_url = default_storage.url(file_name)

            # ذخیره فایل
            if file_data:
                format, filestr = file_data.split(';base64,')
                ext = format.split('/')[-1]
                file_name = default_storage.save(
                    f"chats/files/msg.{ext}",
                    ContentFile(base64.b64decode(filestr))
                )
                file_url = default_storage.url(file_name)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "sender": sender,
                    "text": text,
                    "image": image_url,
                    "file": file_url,
                    "post": post,
                    "event": "message"
                }
            )

        # -------------------------
        # رویداد is_read
        # -------------------------
        elif event_type == "read":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "event": "read",
                    "message_id": data.get("message_id")
                }
            )

        # -------------------------
        # رویداد is_liked
        # -------------------------
        elif event_type == "like":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "event": "like",
                    "message_id": data.get("message_id"),
                    "is_liked": data.get("is_liked")
                }
            )


    async def chat_message(self, event):
        """ ارسال نهایی به کلاینت‌ها """
        await self.send(text_data=json.dumps(event))

    async def chat_read(self, event):
        await self.send(text_data=json.dumps(event))

        # handler پیام لایک شد

    async def chat_like(self, event):
        await self.send(text_data=json.dumps(event))