from django.contrib.auth import get_user_model
from .models import UserProfile,ProfilePicture
from .choices import PrivacyChoices

from typing import Optional

User = get_user_model()

def has_user_any_profiles(user : User):
    return (user.pictures.count()) != 0


def can_user_access_this_field_from_that_user(user : User,target_user : User,target_field : str) -> bool:
    if user == target_user:
        return True
    user_privacy_status = target_user.privacy_settings
    is_in_contacts = target_user in user.contact_users

    if user_privacy_status[target_field] == PrivacyChoices.EVERYONE:
        return True
    
    if user_privacy_status[target_field] == PrivacyChoices.ONLYCONTACTS and is_in_contacts:
        return True


    return False
    

def find_primary_picture_of_user(user : User) -> Optional[ProfilePicture]:
    primary_picture = None
    try :
        primary_picture = user.pictures.get(is_primary = True)
        return primary_picture
    except:
        return None

def get_first_profile_picture_that_isnt_primary(user : User) -> Optional[ProfilePicture]:
    selected_pic = None
    sorted_profile_pictures = user.pictures.order_by("-created_in")
    for pic in sorted_profile_pictures:
        if pic.is_primary:
            continue
        else:
            selected_pic = pic
            break
    if selected_pic: 
        return selected_pic
    

def is_unique_username(username : str)-> bool:
    return not UserProfile.objects.filter(username = username).exists()


