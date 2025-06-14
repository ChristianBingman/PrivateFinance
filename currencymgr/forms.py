from django import forms
from .models import Currency


class CurrencyCreateForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ["full_name", "symbol", "current_price", "fraction_traded"]
