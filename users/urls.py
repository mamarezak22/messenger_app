from django.urls import path
from .views import (GetCodeView,CheckCodeView,SetNameView,GetCodeNewNumberView,CheckCodeNewNumberView,ContactAddView,ContactRemoveView,ContactListView,BlockUserView,UnblockUserView,BlockUserListView,SetAPicturePrimaryProfile,
                     ProfileDetailView,ProfilePictureListView,ProfilePictureDetailView,SettingsView,ProfileUpdateView,SetOnlineStatusView,SetOfflineStatusView,GetMeProfileView)

urlpatterns = [
   path("check-code",CheckCodeView.as_view(),name = "check-code") ,
   path("get-code",GetCodeView.as_view(),name = "get-code"),

   path("set-name",SetNameView.as_view(),name = "set-name"),
   path("getme",GetMeProfileView.as_view(),name="get-me"),

   path("change-number/check-code",CheckCodeNewNumberView.as_view(),name="check-code-for-new-number"),
   path("change-number/get-code",GetCodeNewNumberView.as_view(),name = "get-code-for-new-number"),

   path("profile/",ProfileDetailView.as_view(),name ='profile-detail'),
   path("profile/update",ProfileUpdateView.as_view(),name='update-profile'),
   path("profile/pictures/",ProfilePictureListView.as_view(),name = "get-profile-pictures"),
   path("profile/pictures/<int:id>",ProfilePictureDetailView.as_view(),name = "get-a-profile-picture"),
   path("profile/pictures/<int:id>/set-primary",SetAPicturePrimaryProfile.as_view(),name="set-a-profile-picture-as-primary"),
   path("blocked_users/",BlockUserListView.as_view(),name="get-blocked-users"),
   path("blocked_users/block",BlockUserView.as_view(),name="block a user"),
   path("blocked_users/unblock",UnblockUserView.as_view(),name="unblock a user"),

   path("contacts/",ContactListView.as_view(),name="get-contacts"),
   path("contacts/add",ContactAddView.as_view(),name="add-contact"),
   path("contacts/remove",ContactRemoveView.as_view(),name="delete-contact"),

   path("settings/",SettingsView.as_view(),name='settings'),


   path("set-online/",SetOnlineStatusView.as_view(),name="set-online"),
   path("set-offline/",SetOfflineStatusView.as_view(),name = "set-offline")
   
]