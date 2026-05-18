from django.urls import path
from . import views

urlpatterns=[
    path('user_appoint/',views.user_appoint,name='user_appoint'),
    path('profile_user/',views.user_appoint,name='profile_user'),
]