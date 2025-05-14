from django.views.generic import ListView

from .models import Account


class AccountView(ListView):
    model = Account
    context_object_name = "accounts"
