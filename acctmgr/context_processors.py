from django.http import HttpRequest, HttpResponse
from .models import Account


def account_context(request: HttpRequest) -> HttpResponse:
    return {"accounts": Account.objects.get_accounts()}
