from django.urls import path, include
from django.views.generic import TemplateView

from apps.account import views
from apps.account.views import RegisterView, Search, LogoutView, FollowersList, FollowingList, \
    send_friend_request, RequestList, accept_friend_request, UpdateUser, ActivateView, verify
from common.view import LoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),
    path('profile/', views.UserName.as_view(), name='profile'),
    path('userprofile/', TemplateView.as_view(template_name="account/user-profile.html"), name='user-profile'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
    path('search/', Search.as_view(), name="search"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('send_friend_request/<int:userID>', send_friend_request, name="send friend request"),
    path('accept_friend_request/<int:requestID>', accept_friend_request, name="accept friend request"),
    path('edit/<int:pk>', UpdateUser.as_view(), name='edit'),
    path('My_follower/', FollowersList.as_view(), name="my_follower"),
    path('My_following/', FollowingList.as_view(), name="my_following"),
    path('Request_List/', RequestList.as_view(), name="Request_List"),
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='account/change-password.html',
            success_url='/profile/'
        ),
        name='change-pass'
    ),
    path('user_list/', views.UserList.as_view(), name='user_list'),
    path('<int:pk>/', include([
        path('', views.UserDetail.as_view(), name='user_detail'),
    ]
    ), ),
    path('verify/', verify, name='verify'),
]
