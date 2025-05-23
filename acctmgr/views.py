from django.shortcuts import render, get_object_or_404

from .models import Account


def index(request, pk=None):
    context = {"accounts": Account.objects.get_accounts()}
    if pk is not None:
        context["transaction_entries"] = get_object_or_404(
            Account, pk=pk
        ).transactionentry_set.all()
    return render(request, "acctmgr/account_list.html", context)
