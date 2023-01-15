from django import forms
from django.forms import PasswordInput

from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'avatar', 'phone')


class ChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'avatar', 'phone')


class PassChangeForm(PasswordChangeForm):
    error_css_class = 'has-error'
    error_messages = {'password_incorrect': 'The old password is not correct. Try again.'}
    old_password = forms.CharField(required=True,
                                   label='Password',
                                   widget=PasswordInput(attrs={
                                       'class': 'form-control', 'placeholder': 'Old password',
                                   }),
                                   error_messages={
                                       'required': 'Password cannot be empty'})

    new_password1 = forms.CharField(required=True, label='Password',
                                    widget=PasswordInput(attrs={
                                        'class': 'form-control', 'placeholder': 'New password', }),
                                    error_messages={
                                        'required': 'Password cannot be empty'})
    new_password2 = forms.CharField(required=True,
                                    label='Password (Repeat)',
                                    widget=PasswordInput(attrs={
                                        'class': 'form-control', 'placeholder': 'Repeat new password',
                                    }),
                                    error_messages={
                                        'required': 'Password cannot be empty'
                                    })


