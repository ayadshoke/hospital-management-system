from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username','email','password1','password2')



