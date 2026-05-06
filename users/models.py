from django.db import models
from django.contrib.auth.models import AbstractBaseUser


from datetime import datetime

from .functions import get_upload_path_for_profile_image 
from .validators import validate_phone_number,validate_user_name
from .managers import UserManager
# Create your models here.

class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=11, unique=True,validators=[validate_phone_number])
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    joined_in = models.DateTimeField(default = datetime.now())

    objects = UserManager()
    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.phone_number




class UserProfile(models.Model):
    user = models.ForeignKey(User,related_name="profile",on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    pictures = models.ForeignKey("Picture",related_name="pictures",on_delete=models.SET_NULL,null = True)
    username = models.CharField(max_length=128,validators=[validate_user_name],null=True,unique = True)
    about_me = models.TextField(null=True)
    is_online = models.BooleanField(default = False)
    last_seen = models.DateTimeField(default=datetime.now())

    # def get_picture_upload_path(self):
    #     return f"uploads/pictures/{self.name}/"

    def __str__(self):
        return f"profile of {self.user}"

class Picture(models.Model):
    content = models.ImageField(upload_to=get_upload_path_for_profile_image)

