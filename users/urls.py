from django.urls import include ,path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import GetCodeView,ChangeProfileDetailView,CheckCodeView,SetProfileView 

urlpatterns = [
   path("token/",TokenObtainPairView.as_view(),name = "get-token"),
   path("token/refresh/",TokenRefreshView.as_view(),name = "refresh-token"),
   path("code/check",CheckCodeView.as_view(),name = "check-code") ,
   path("code/get",GetCodeView.as_view(),name = "get-code"),
   path("profile/set",SetProfileView.as_view(),name="set-profile"),
   path("profile/change",ChangeProfileDetailView.as_view(),name="change-profile"),
]