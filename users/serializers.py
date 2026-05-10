from rest_framework import serializers
from django.contrib.auth import get_user_model

from .validators import validate_phone_number
from .models import UserProfile,ProfilePicture,UserPrivacySettings
from .helpers import can_user_access_this_field_from_that_user 

User = get_user_model()

#input validation serialziers
class GetCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators = [validate_phone_number,])


class CheckCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators = [validate_phone_number,])
    code = serializers.IntegerField()


class SetNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length = 128)


#output model serialziers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone_number","is_online","last_seen",)
    
    def get_phone_number(self,obj):
        request = self.context.get("request")

        if request:
            user = request.user
            
            #a flag that shows if user looking for himself profile or for it's contacts.
            can_access = can_user_access_this_field_from_that_user(user = user,
                                                      target_user=obj.user,
                                                      target_field="is_online") 
            
            if can_access:
                return obj.is_online
        return None
        

    def get_is_online(self,obj): 
        request = self.context.get("request")

        if request:
            user = request.user
            
            #a flag that shows if user looking for himself profile or for it's contacts.
            can_access = can_user_access_this_field_from_that_user(user = user,
                                                      target_user=obj.user,
                                                      target_field="is_online") 
            
            if can_access:
                return obj.is_online
        return None
    
    def get_last_seen(self,obj):
        request = self.context.get("request")

        if request:
            user = request.user
            
            #a flag that shows if user looking for himself profile or for it's contacts.
            can_access = can_user_access_this_field_from_that_user(user = user,
                                                      target_user=obj.user,
                                                      target_field="last_seen") 
            
            if can_access:
                return obj.is_online
        return None
    


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ["content","is_primary"]

class UserProfileOutputSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    pictures = ProfilePictureSerializer(many = True)
    class Meta:
        model = UserProfile 
        fields = ["user","name","username","about_me","pictures"]
    
    def get_pictures(self,obj):
        request = self.context.get("request")

        if request:
            user = request.user
            
            #a flag that shows if user looking for himself profile or for it's contacts.
            can_access = can_user_access_this_field_from_that_user(user = user,
                                                      target_user=obj.user,
                                                      target_field="profile_pic") 
            
            if can_access:
                return obj.is_online
        return None


class UserProfileInputSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    pictures = ProfilePictureSerializer(many = True)
    class Meta:
        model = UserProfile 
        fields = ["name","username","about_me"]


class PictureInputSerializer(serializers.Serializer):
    picture = serializers.ImageField()


class PrivacySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPrivacySettings 
        fields = ["__all__"]