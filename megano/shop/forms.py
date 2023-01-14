from django import forms


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





