from django import forms
from .models import Feedback


class PriceForm(forms.Form):
    price = forms.CharField(max_length=20)


class DeliveryForm(forms.Form):
    delivery = forms.CharField(max_length=20)
    address = forms.CharField(max_length=20)
    city = forms.CharField(max_length=20)


class ChoicePaymentForm(forms.Form):
    payment_way = forms.CharField(max_length=4)


class CardForm(forms.Form):
    card = forms.CharField()


class CommentForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'feedback']


class AuthCommentForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ['feedback']




