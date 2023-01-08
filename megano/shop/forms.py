from django import forms


class PriceForm(forms.Form):
    price = forms.CharField(max_length=20)




