import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time notifications.
    """
    async def connect(self):
        """
        Called when the WebSocket is handshaking as part of the connection process.
        """
        self.user = self.scope["user"]
        
        # Reject the connection if the user is not authenticated
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Add user to their personal group
        await self.channel_layer.group_add(
            f'user_{self.user.id}',
            self.channel_name
        )
        
        # Add admin users to the admin group
        if await self.is_admin_user(self.user):
            await self.channel_layer.group_add(
                'admin_notifications',
                self.channel_name
            )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Remove user from their personal group
        await self.channel_layer.group_discard(
            f'user_{self.user.id}',
            self.channel_name
        )
        
        # Remove admin users from the admin group
        if await self.is_admin_user(self.user):
            await self.channel_layer.group_discard(
                'admin_notifications',
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Called when we get a text frame from the client.
        """
        # We don't expect to receive messages from the client
        pass
    
    async def notification_message(self, event):
        """
        Called when a notification is sent to a group.
        """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'ticket_id': event.get('ticket_id'),
            'refresh': event.get('refresh', False),
        }))
    
    @database_sync_to_async
    def is_admin_user(self, user):
        """
        Check if a user is an admin or staff.
        """
        return user.is_admin or user.is_staff
