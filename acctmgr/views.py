from django.shortcuts import render

from .models import Account

def index(request):
    context = {"accounts": Account.objects.get_accounts()}
    return render(request, "acctmgr/account_list.html", context)
