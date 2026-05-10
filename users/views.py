#user login 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


User = get_user_model()

from .models import User,UserProfile,ProfilePicture,UserPrivacySettings
from .helpers import has_user_any_profiles 
from .serializers import GetCodeSerializer,CheckCodeSerializer,SetNameSerializer,UserProfileOutputSerializer,UserProfileInputSerializer,PictureInputSerializer,ProfilePictureSerializer,PrivacySettingsSerializer

import random

#this view not really send the code.and it's for educational purpouses.
#actually it return the code in api response.
class GetCodeView(APIView):
    permission_classes = [AllowAny,]
    def post(self,request):
        serializer = GetCodeSerializer(data = request.data) 
        serializer.is_valid(raise_exception=True)

        # phone_number = serializer.validated_data["phone_number"]
        #first check if a code generated for this phone_number before.
        #if that's the case . then we don't send anymore code.
        sent_before_code = cache.get(f"code for {phone_number}")
        if sent_before_code:
            return Response({"detail" : "code has been sent before"},status = 200)

        else :

            code = random.randint(10000,99999) 
            cache.set(f"code for {phone_number}",str(code),timeout=180)

            return Response({"code" : code},status = 200)


class CheckCodeView(APIView):
    permission_classes = [AllowAny,]
    def post(self, request):
        serializer = CheckCodeSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        user_given_code = serializer.validated_data["code"]

        #we check that is a user exist by this phone_number before and by that we set a flag.


        real_code = cache.get(f"code for {phone_number}")

        if not real_code:
            return Response({"detail" : "code expired"},
            status = 400)

        elif int(real_code) != user_given_code:
            return Response({"detail" : "code not valid"},
                            status = 400)

        if not User.objects.filter(phone_number = phone_number).exists():
            user = User.objects.create(phone_number = phone_number)
            status = 201
        else:
            status = 200
            user = User.objects.get(phone_number = phone_number)
            #TODO: it must acess to user contacts. and add them to user.contacts.
            #it can been set when this app become an mobile app.
            # user.contacts = User.objects.filter()

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh" : str(refresh),
            "access" : str(refresh.access_token),
        },status = status)

class SetNameView(APIView):
    def post(self,request):
        serializer = SetNameSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        #create related objects blonged to our logged in user.
        UserProfile.objects.create(user = request.user,name = serializer.validated_data["name"])
        UserPrivacySettings.objects.create(user = request.user)
        return Response({"detail" : "your profile name has been set"},status = 201)

#this two views must runned in a sequence.
#after user phone_number logged in. now it's time to user name has been given and it's profile object been created in DB.

class AddProfilePictureView(APIView):
    def post(self,request):
        user = request.user
        serializer = PictureInputSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user_has_profile = has_user_any_profiles(user)

        ProfilePicture.objects.create(owner = user,
                                                content = request.data["picture"],
                                                is_primary = not user_has_profile)
        return Response({"detail" : "your profile picture has been sucsessfully add"},status = 200)


class ProfilePictureListView(APIView):
    def get(self,request):
        user = request.user
        pictures = user.pictures

        serializer = ProfilePictureSerializer(pictures , many = True)

        return Response(serializer.data,
                        status = 200)



class ProfilePictureDetailView(APIView):
    def get(self,request,id):
        user = request.user
        picture = get_object_or_404(ProfilePicture,user = user,id = id)

        serializer = ProfilePictureSerializer(picture)

        return Response(serializer.data,
                        status = 200)

class SetAPicturePrimaryProfile(APIView):
    def post(self,request,id):
        user = request.user
        picture = get_object_or_404(ProfilePicture,user = user,id = id)

        if picture.is_primary == True:
            detail = "it's already primary picture"
            status = 400

        else:
            primary_profile_picture_of_user = find_primary_picture_of_user(user = user)

            primary_profile_picture_of_user.is_primary = False
            picture.is_primary = True
            detail = "primary picture has been change successfully."
            status = 200

        return Response({"detail" : detail},
                        status = status)
 





class ProfileDetailView(APIView):
    def get(self,request):

        if not "id" in request.data or not "phone_number" in request.data:
            return Response({"detail" : "for getting profile you must send id or phone in request"},
                            status = 400)
        
        if "id" in request.data:
            user_profile = get_object_or_404(UserProfile,user__pk = request.data.get("id"))

        elif "phone_number" in request.data:
            user_profile = get_object_or_404(UserProfile,user__phone_number = request.data.get("phone_number"))

        #if the profile that user trying to reach is himself profile.
        serializer = UserProfileOutputSerializer(user_profile,
                                            context = {"request" : request}) 
        return Response(serializer.data,
                        status = 200)

    def put(self,request):
        user_profile = request.user.profile
        #update object
        serializer = UserProfileInputSerializer(user_profile , data = request.data,partial = True) 
        serializer.is_valid(raise_exception=True)
        #save object
        serializer.save()
        return Response({"detail" : "profile changed succsessfully"},
                        status = 200)


    
#get all blocked users(get)
#block a user(post)
#unblock a user(delete)
#same things for ContactView
class BlockUserListView(APIView):

    def get(self,request):
        user = request.user
        blocked_users = user.blocked_by_users
        blocked_users_profile = blocked_users.profile
        serializer = UserProfileOutputSerializer(blocked_users_profile,
                                                 many = True,
                                                 context = {"request" : request})
        return Response(serializer.data,
                        status = 200)

class BlockUserView(APIView):
    def post(self,request):
        request_sender_user = request.user
        query_params = request.query_params

        if query_params.get("id"): 
            target_user = get_object_or_404(User,pk = query_params["id"]) 

        elif query_params.get("phone"):
            target_user = get_object_or_404(User,phone_number = query_params["phone"]) 

        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)

        if target_user in request_sender_user.blocked_by_users:
            return Response({"detail" : "the user is already blocked"},
                            status = 400)
        
        request_sender_user.contact_users.add(target_user)
        return Response({"detail" : "user blocked successfully"},
                        status = 200)


class UnblockUserView(APIView):
    #it get user_id and if it's in blocked users remove them.
    def delete(self,request):
        request_sender_user = request.user
        query_params = request.query_params

        if query_params.get("id"): 
            target_user = get_object_or_404(User,pk = query_params["id"]) 

        elif query_params.get("phone"):
            target_user = get_object_or_404(User,phone_number = query_params["phone"]) 

        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)

        if target_user not in request_sender_user.blocked_by_users:
            return Response({"detail" : "the user not blocked before"},
                            status = 400)
        
        request_sender_user.contact_users.add(target_user)
        return Response({"detail" : "user unblocked successfully."},
                        status = 200)
        



class ContactListView(APIView):

    def get(self,request):
        user = request.user
        contacts = user.contact_users
        contacts_profile = contacts.profile
        serializer = UserProfileOutputSerializer(contacts_profile,
                                                 many = True,
                                                 context = {"request" : request})
        return Response(serializer.data,
                        status = 200)


#users/contact?id=id or phone=phone
#olaviat is with id.
class ContactAddView(APIView):
    def post(self,request):
        request_sender_user = request.user
        query_params = request.query_params
        if query_params.get("id"): 
            target_user = get_object_or_404(User,pk = query_params["id"]) 

        elif query_params.get("phone"):
            target_user = get_object_or_404(User,phone_number = query_params["phone"]) 

        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)

        if target_user in request_sender_user.contact_users:
            return Response({"detail" : "the user is already a contact"},
                            status = 400)
        
        request_sender_user.contact_users.add(target_user)
        return Response({"detail" : "user successfully added to contacts"},
                        status = 200)

#TODO:another view to add all contacts based on phone_numbers of android device.


class ContactRemoveView(APIView): 
    def delete(self,request):
        request_sender_user = request.user
        query_params = request.query_params
        if query_params.get("id"): 
            target_user = get_object_or_404(User,pk = query_params["id"]) 

        elif query_params.get("phone"):
            target_user = get_object_or_404(User,phone_number = query_params["phone"]) 

        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)

        if target_user not in request_sender_user.contact_users:
            return Response({"detail" : "the user is not a contact"},
                            status = 400)
        
        request_sender_user.contact_users.remove(target_user)
        return Response({"detail" : "user successfully removed from contacts"},
                        status = 200)


class SettingsView(APIView):
    #get the settings
    def get(self,request):
        settings = request.user.privacy_settings
        serializer = PrivacySettingsSerializer(settings) 
        return Response(serializer.data,
                        status = 200)

    #change the settings 
    def put(self,request):
        settings = request.user.privacy_settings
        serializer = PrivacySettingsSerializer(settings,data = request.data,partial = True) 
        return Response(serializer.data,
                        status = 200)


class GetCodeNewNumberView(APIView):
    def post(self,request):
        serializer = GetCodeSerializer(data = request.data) 
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        # phone_number = serializer.validated_data["phone_number"]
        #first check if a code generated for this phone_number before.
        #if that's the case . then we don't send anymore code.
        sent_before_code = cache.get(f"code for {phone_number}")
        if sent_before_code:
            return Response({"detail" : "code has been sent before"},status = 200)

        if User.objects.filter(phone_number = phone_number).exists():
             return Response({"detail" : "this phone number has a account already"},
                             status = 400)



        code = random.randint(10000,99999) 
        cache.set(f"code for {phone_number}",str(code),timeout=180)

        return Response({"code" : code},status = 200)


class CheckCodeNewNumberView(APIView):
    def post(self, request):
        user = request.user
        serializer = CheckCodeSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        user_given_code = serializer.validated_data["code"]

        #we check that is a user exist by this phone_number before and by that we set a flag.


        real_code = cache.get(f"code for {phone_number}")

        if not real_code:
            return Response({"detail" : "code expired"},
            status = 400)

        if int(real_code) != user_given_code:
            return Response({"detail" : "code not valid"},
                            status = 400)

        if User.objects.filter(phone_number = phone_number).exists():

            return Response({"detail" : "this phone number has a account already"},
                            status = 400)

        user.phone_number = phone_number 
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh" : str(refresh),
            "access" : str(refresh.access_token),
        },status = 200)


# class LogOutView(APIView):
#     def post(self,request):
#         ...