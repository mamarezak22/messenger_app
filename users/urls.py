from django.urls import path
from .views import (GetCodeView,CheckCodeView,SetNameView,GetCodeNewNumberView,CheckCodeNewNumberView,ContactAddView,ContactRemoveView,ContactListView,BlockUserView,UnblockUserView,BlockUserListView,SetAPicturePrimaryProfile,
                     ProfileDetailView,AddProfilePictureView,ProfilePictureListView,ProfilePictureDetailView)

urlpatterns = [
   path("check-code",CheckCodeView.as_view(),name = "check-code") ,
   path("get-code",GetCodeView.as_view(),name = "get-code"),
   path("set-name",SetNameView.as_view(),name = "set-name"),
   path("change-number/check-code",CheckCodeNewNumberView.as_view(),name="check-code-for-new-number"),
   path("change-number/get-code",GetCodeNewNumberView.as_view(),name = "get-code-for-new-number"),
   path("profile/",ProfileDetailView.as_view(),name ='get-a-profile'),
   path("profile-pictures/",ProfilePictureListView.as_view(),name = "get-profile-pictures"),
   path("profile/pictures/<int:id>",ProfilePictureDetailView.as_view(),name = "get-a-profile-picture"),
   path("profile-pictures/add",AddProfilePictureView.as_view(),name="add-profile"),
   path("profile-pictures/set-primary/<int:id>",SetAPicturePrimaryProfile.as_view(),name="set-a-profile-picture-as-primary"),
   path("contacts/",ContactListView.as_view(),name="get-contacts"),
   path("contacts/add",ContactAddView.as_view(),name = "add-contact"),
   path("contacts/remove",ContactRemoveView.as_view(),name = "remove-contact"),
   path("blocks/",BlockUserListView.as_view(),name="get-blocked-users"),
   path("blocks/add",BlockUserView.as_view(),name = "block-a-user"),
   path("blocks/remove",UnblockUserView.as_view(),name = "unblock-a-user"),
]