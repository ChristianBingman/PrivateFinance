from django import forms
from .models import Account


class AccountCreateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            "name",
            "currency",
            "acct_type",
            "description",
            "parent",
            "placeholder",
        ]
