from models import User

def has_user_any_profiles(user : User):
    return len(user.pictures) != 0