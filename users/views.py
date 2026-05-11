#user login 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken 
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.parsers import FormParser,MultiPartParser


User = get_user_model()

from .models import User,UserProfile,ProfilePicture,UserPrivacySettings
from .helpers import has_user_any_profiles ,get_first_profile_picture_that_isnt_primary,find_primary_picture_of_user,is_unique_username
from .serializers import GetCodeSerializer,CheckCodeSerializer,SetNameSerializer,UserProfileOutputSerializer,UserProfileInputSerializer,PictureInputSerializer,ProfilePictureSerializer,PrivacySettingsSerializer

import random

#this view not really send the code.and it's for educational purpouses.
#actually it return the code in api response.
class GetCodeView(APIView):
    permission_classes = [AllowAny,]
    def post(self,request):
        serializer = GetCodeSerializer(data = request.data) 
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        # phone_number = serializer.validated_data["phone_number"]
        #first check if a code generated for this phone_number before.
        #if that's the case . then we don't send anymore code.
        sent_before_code = cache.get(f"code for {phone_number}")

        if sent_before_code:
            return Response({"code" : sent_before_code},status = 200)

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

        if UserProfile.objects.filter(user = request.user).exists():
            return Response({"detail" : "you set name before"},
                            status = 400)

        #create related objects blonged to our logged in user.
        UserProfile.objects.create(user = request.user,name = serializer.validated_data["name"])
        UserPrivacySettings.objects.create(user = request.user)
        return Response({"detail" : "your profile name has been set"},status = 201)

#this two views must runned in a sequence.
#after user phone_number logged in. now it's time to user name has been given and it's profile object been created in DB.
     
class ProfilePictureListView(APIView):
    parser_classes = (MultiPartParser,FormParser)
    def get(self,request):
        user = request.user
        pictures = user.pictures

        serializer = ProfilePictureSerializer(pictures , many = True)

        return Response(serializer.data,
                        status = 200)
    def post(self,request):
        user = request.user
        picture = request.FILES.get("picture")
        if not picture: 
            return Response({"detail" : "send a picture"},
                            status = 400)

        data = {}
        data["picture"] = picture
        serializer = PictureInputSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        user_has_profile = has_user_any_profiles(user)

        ProfilePicture.objects.create(owner = user,
                                                content = serializer.validated_data["picture"],
                                                is_primary = not user_has_profile)
        return Response({"detail" : "your profile picture has been sucsessfully add"},status = 200)




class ProfilePictureDetailView(APIView):
    def get(self,request,id):
        user = request.user
        profile_picture = get_object_or_404(ProfilePicture,owner = user,id = id)
        

        serializer = ProfilePictureSerializer(profile_picture)

        return Response(serializer.data,
                        status = 200)
    
    def delete(self,request,id):
       user = request.user
       profile_picture = get_object_or_404(ProfilePicture,owner = user,id = id)

       if profile_picture.is_primary :
            future_primary_profile_picture = get_first_profile_picture_that_isnt_primary(user = user)
            if future_primary_profile_picture:
                future_primary_profile_picture.is_primary = True
                future_primary_profile_picture.save()

       profile_picture.delete() 
       return Response({"detail" : "it has been successfully deleted"},
                        status = 200)



class SetAPicturePrimaryProfile(APIView):
    def post(self,request,id):
        user = request.user
        picture = get_object_or_404(ProfilePicture,owner = user,id = id)

        if picture.is_primary == True:
            detail = "it's already primary picture"
            status = 400

        else:
            primary_profile_picture_of_user = find_primary_picture_of_user(user = user)
            if primary_profile_picture_of_user:
                primary_profile_picture_of_user.is_primary = False
                primary_profile_picture_of_user.save()
            picture.is_primary = True
            picture.save()
            detail = "primary picture has been change successfully."
            status = 200

        return Response({"detail" : detail},
                        status = status)
 





class ProfileDetailView(APIView):
    def post(self,request):
        id = request.data.get("id")
        phone_number = request.data.get("phone_number")
        username = request.data.get("username")

        if not id and not phone_number and not username:
            return Response({"detail" : "for getting profile you must send id or phone or username in request"},
                            status = 400)
        
        if id:
            user_profile = get_object_or_404(UserProfile,user__pk = request.data.get("id"))

        elif phone_number: 
            user_profile = get_object_or_404(UserProfile,user__phone_number = request.data.get("phone_number"))

        else: 
            user_profile = get_object_or_404(UserProfile,username = request.data.get("username"))
       #if the profile that user trying to reach is himself profile.
        serializer = UserProfileOutputSerializer(user_profile,
                                            context = {"request" : request}) 
        return Response(serializer.data,
                        status = 200)

class ProfileUpdateView(APIView):
    def put(self,request):
        user_profile = request.user.profile
        #update object
        serializer = UserProfileInputSerializer(user_profile , data = request.data,partial = True) 
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get("username") and is_unique_username(user_profile.username) and serializer.validated_data["username"]!= user_profile.username:
            return Response({"detail" : "username is been used"},
                            status = 400)

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

        blocked_users_qs = user.blocked_by_users.all()  # the users who blocked you

        # Option A: if UserProfile is OneToOne with user:
        profiles_qs = UserProfile.objects.filter(user__in=blocked_users_qs)
        serializer = UserProfileOutputSerializer(profiles_qs,
                                                 many = True,
                                                 context = {"request" : request})
        return Response(serializer.data,
                        status = 200)

class BlockUserView(APIView):
    def post(self,request):
        request_sender_user = request.user

        id = request.data.get("id")
        phone = request.data.get("phone_number")
        username = request.data.get("username")

        if id: 
            target_user = get_object_or_404(User,pk = id) 

        elif phone :
            target_user = get_object_or_404(User,phone_number = phone) 
        
        elif username:
            target_user = get_object_or_404(User,profile__username = username)
        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)
 
        if target_user == request_sender_user:
            return Response({"detail" : "you can not do this operation on yourself"},
                            status = 400)

        if target_user in request_sender_user.blocked_by_users.all():
            return Response({"detail" : "the user is already blocked"},
                            status = 400)
        
        request_sender_user.blocked_by_users.add(target_user)
        request_sender_user.save()
        return Response({"detail" : "user blocked successfully"},
                        status = 200)


class UnblockUserView(APIView):
    #it get user_id and if it's in blocked users remove them.
    def delete(self,request):
        request_sender_user = request.user

        id = request.data.get("id")
        phone = request.data.get("phone_number")
        username = request.data.get("username")

        if id: 
            target_user = get_object_or_404(User,pk = id) 

        elif phone :
            target_user = get_object_or_404(User,phone_number = phone) 
        
        elif username:
            target_user = get_object_or_404(User,profile__username = username)
        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)
        
        if target_user == request_sender_user:
            return Response({"detail" : "you can not do this operation on yourself"},
                            status = 400)
        if target_user not in request_sender_user.blocked_by_users.all():
            return Response({"detail" : "the user not blocked before"},
                            status = 400)
        
        request_sender_user.blocked_by_users.remove(target_user)
        request_sender_user.save()
        return Response({"detail" : "user unblocked successfully."},
                        status = 200)
        



class ContactListView(APIView):

    def get(self,request):
        user = request.user

        contacts_qs = user.blocked_by_users.all()  # the users who blocked you

        # Option A: if UserProfile is OneToOne with user:
        profiles_qs = UserProfile.objects.filter(user__in=contacts_qs)
        serializer = UserProfileOutputSerializer(profiles_qs,
                                                 many = True,
                                                 context = {"request" : request})
        return Response(serializer.data,
                        status = 200)

class ContactAddView(APIView):
    def post(self,request):
        request_sender_user = request.user

        id = request.data.get("id")
        phone = request.data.get("phone_number")
        username = request.data.get("username")

        if id: 
            target_user = get_object_or_404(User,pk = id) 

        elif phone :
            target_user = get_object_or_404(User,phone_number = phone) 
        
        elif username:
            target_user = get_object_or_404(User,profile__username = username)
        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)
 
        if target_user == request_sender_user:
            return Response({"detail" : "you can not do this operation on yourself"},
                            status = 400)


        if target_user in request_sender_user.contact_users.all():
            return Response({"detail" : "the user is already a contact"},
                            status = 400)
        
        request_sender_user.contact_users.add(target_user)
        request_sender_user.save()
        return Response({"detail" : "user successfully added to contacts"},
                        status = 200)

#TODO:another view to add all contacts based on phone_numbers of android device.


class ContactRemoveView(APIView): 
    def delete(self,request):
        request_sender_user = request.user

        if request.data.get("id"): 
            target_user = get_object_or_404(User,pk = request.data["id"]) 

        elif request.data.get("phone"):
            target_user = get_object_or_404(User,phone_number = request.data["phone"]) 
        
        elif request.data.get("username"):
            target_user = get_object_or_404(User,profile__username = request.data.get("username"))
        
        else:
            return Response({"detail" : "enter id or phone in query params for finding a user"},
                            status = 400)
 
        if target_user == request_sender_user:
            return Response({"detail" : "you can not do this operation on yourself"},
                            status = 400)

        if target_user not in request_sender_user.contact_users.all():
            return Response({"detail" : "the user is not a contact"},
                            status = 400)
        
        request_sender_user.contact_users.remove(target_user)
        request_sender_user.save()
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
        #in json request body for values must send this values {EVERYONE,ONLY_CONTACTS,NOONE}
        serializer = PrivacySettingsSerializer(settings,data = request.data,partial = True) 
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status = 200)


class GetCodeNewNumberView(APIView):
    def post(self,request):
        serializer = GetCodeSerializer(data = request.data) 
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        if phone_number == request.user.phone_number:
            return Response({"detail" : "it is same as your old phone number"},
                            status = 400)
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

class SetOnlineStatusView(APIView):
    def post(self,request):
        user = request.user
        if user.is_online:
            return Response({"detail" : "user already is online"},
                            status = 400)
        user.is_online = True
        user.save()
        return Response({"detail": "it has been successfully changed"},
                        status = 200)
    
class SetOfflineStatusView(APIView):
    def post(self,request):
        user = request.user
        if not user.is_online:
            return Response({"detail" : "user already is offline"},
                            status = 400)
        user.is_online = False
        user.last_seen = timezone.now()
        user.save()
        return Response({"detail": "it has been successfully changed"},
                        status = 200)
    


class GetMeProfileView(APIView):
    def get(self,request):
        profile = request.user.profile
        serilaizer =  UserProfileOutputSerializer(profile) 
        return Response(serilaizer.data,
                        status = 200)
