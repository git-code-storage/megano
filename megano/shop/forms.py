from django import forms
from .models import Feedback


class PriceForm(forms.Form):
    price = forms.CharField(max_length=20)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'feedback']


class AuthCommentForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ['feedback']




