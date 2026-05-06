from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils import timezone


from .functions import get_upload_path_for_profile_image 
from .validators import validate_phone_number,validate_user_name
from .managers import UserManager
# Create your models here.

class User(AbstractBaseUser):
    id = models.BigAutoField()
    phone_number = models.CharField(max_length=11, unique=True,validators=[validate_phone_number])
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    joined_in = models.DateTimeField(auto_now_add = True)

    #because a user can be contact of another user.but it's not 2way.its 1way.
    contacts = models.ManyToManyField(to = "User",related_name="contact_of",symmetrical=False)
    blocked_users = models.ManyToManyField(to = "User",related_name="blocked_by",symmetrical=False)

    is_online = models.BooleanField(default = False)
    last_seen = models.DateTimeField(default = timezone.now())

    objects = UserManager()
    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.phone_number




class UserProfile(models.Model):
    user = models.OneToOneField(User,related_name="profile",on_delete=models.CASCADE,primary_key=True)
    name = models.CharField(max_length=128)
    username = models.CharField(max_length=128,validators=[validate_user_name],null=True,unique = True)
    about_me = models.TextField(null=True)

    # def get_picture_upload_path(self):
    #     return f"uploads/pictures/{self.name}/"

    def __str__(self):
        return f"profile of {self.user}"

class ProfilePicture(models.Model):
    owner = models.ForeignKey(User,related_name="pictures",on_delete=models.CASCADE)
    id = models.BigAutoField(primary_key=True)
    content = models.ImageField(upload_to=get_upload_path_for_profile_image)
    is_primary = models.BooleanField(default=False)

