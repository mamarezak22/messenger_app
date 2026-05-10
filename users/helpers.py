from django.contrib.auth import get_user_model
from .models import UserProfile,ProfilePicture
from .choices import PrivacyChoices

User = get_user_model()

def has_user_any_profiles(user : User):
    return len(user.pictures) != 0


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
    

def find_primary_picture_of_user(user : User) -> ProfilePicture:
    primary_picture = None
    for picture in user.pictures:
        if picture.is_primary == True:
            primary_picture = picture
            break
    return primary_picture
