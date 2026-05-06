from django.db import models
from users.models import User
from django.utils import timezone

message_types = (
    ("text","text"),
    ("document","document"),
)

#for now all messeges have text type.

class Chat(models.Model):
    id = models.BigAutoField(primary_key=True)
    participants = models.ManyToManyField(User,through = "ChatParticipant",related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return f"chat with {self.id} with this participants.\n{self.participants}"

#in case we want to add groups to our app to.
class ChatParticipant(models.Model):
    chat = models.ForeignKey(Chat,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    # add role, muted_until, last_read_message, etc.



class Message(models.Model):
    chat = models.ForeignKey(Chat,related_name="messages",on_delete=models.CASCADE)
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(User,on_delete=models.SET_NULL,null = True,related_name = "sent_messages")
    receiver = models.ForeignKey(User,on_delete=models.SET_NULL,null = True,related_name="recieved_messages")
    text = models.TextField(null = True) 
    # content = models.
    sent_in = models.DateTimeField(auto_now_add = True)
    is_edited = models.BooleanField(default = False)
    is_pinned = models.BooleanField(default=False)
    message_type = models.CharField(choices = message_types,default="text")
    is_a_reply = models.BooleanField(default=False)
    replied_to_messege = models.ForeignKey("Message",on_delete=models.SET_NULL,null = True)
    is_deleted_for_everyone = models.BooleanField(default = False)
    deleted_at = models.DateTimeField(null = True)
    # forwarded_from_chat = 

    def __str__(self) -> str:
        if self.message_type == "text":
            return f"{self.text} send from {self.sender} to {self.receiver}"
        else:
            raise ValueError("a messege can't be not text for now.")

class MessageStatus(models.Model):
    message = models.ForeignKey(Message, related_name='statuses', on_delete=models.CASCADE,primary_key=True)
    user = models.ForeignKey(User, related_name='message_statuses', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted_for_user = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)


