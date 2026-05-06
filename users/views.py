#user login 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

from validators import validate_phone_number
from serializers import UserSerializer
from models import User,UserProfile,ProfilePicture
from helpers import has_user_any_profiles 

import random

class GetCodeView(APIView):
    def post(self,request):
        #checking phone_number first.
        phone_number = request.phone_number
        try : 
            validate_phone_number(phone_number)
        except:
            return Response({"detail" : "your phone number isn't valid man."},status = 400)
        #then give our user a code.

        code = random.randint(10000,99999) 
        cache.set(f"code for {phone_number}",str(code),timeout=180)

        return Response({"detail" : "the code has been sent"},status = 200)


class CheckCodeView(APIView):
    def post(self, request):
        phone_number = request.data["phone_number"]
        user_given_code = request.data["code"]

        #we check that is a user exist by this phone_number before and by that we set a flag.


        real_code = cache.get(f"code for {phone_number}")

        if not real_code:
            return Response({"detail" : "code expired"},
            status = 400)

        elif real_code != user_given_code:
            return Response({"detail" : "code not valid"},
                            status = 400)

        else:
            user = User.objects.create(phone_number = phone_number)
            #TODO: it must acess to user contacts. and add them to user.contacts.
            #it can been set when this app become an mobile app.
            # user.contacts = User.objects.filter()

        refresh = TokenObtainPairSerializer.get_token(user)
        return Response({
            "refresh" : str(refresh),
            "access" : str(refresh.access_token),
        },status = 200)
    
class SetProfileView(APIView):
    permission_classes = (IsAuthenticated,) 
    def post(self,request):
        UserProfile.objects.create(name = request.data["name"])
        return Response({"detail" : "your profile name has been set"},status = 200)

#this two views must runned in a sequence.
#after user phone_number logged in. now it's time to user name has been given and it's profile object been created in DB.

class SetProfilePictureView(APIView):
    def post(self,request):
        permission_classes = (IsAuthenticated,) 
        user = request.user
        user_profile = user.profile
        user_has_profile = has_user_any_profiles(user)

        picture = ProfilePicture.objects.create(owner = user,
                                                content = request.data["picture"],
                                                is_primary = not user_has_profile)
        return Response({"detail" : "your profile picture has been sucsessfully add"},status = 200)


class SetAPicturePrimaryProfile(APIView):
    ...




class ProfileDetailView(APIView):

    permission_classes = (IsAuthenticated,) 

    ...

class BlockUserView(APIView):

    permission_classes = (IsAuthenticated,) 

    ...

class ContactView(APIView):

    permission_classes = (IsAuthenticated,) 

    ...

class UserDetailView(APIView):
    permission_classes = (IsAuthenticated,) 
    def get(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data , 
                        status = 200)

