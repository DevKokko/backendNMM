# chat/urls.py
from django.urls import path

from . import views as vs
from rest_framework_jwt.views import obtain_jwt_token


urlpatterns = [
    path('users/signup', vs.UserCreate.as_view(),name='user-signup'),
    path('users/signin', vs.UserLogin.as_view(),name='user-signin'),
    path('users/update', vs.ChangeUserInfo.as_view(),name='user-update'),
    path('user', vs.GetUserInfo.as_view(),name='user-info'),
    path('verify_account', vs.VerifyAccount.as_view(),name='verify-account'),
    path('admin/users/update', vs.AdminUpdateUser.as_view(),name='admin-user-update'),
    # path('lboard/nmm', vs.LeaderboardViews.NMM_Leaderboard.as_view(),name='user-lboard'),
]