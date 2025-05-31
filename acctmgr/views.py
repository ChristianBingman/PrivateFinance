from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest

from .models import Account
from ledger.forms import TransactionCreateForm


def index(request: HttpRequest, pk=None):
    context = {
        "accounts": Account.objects.get_accounts(),
        "transaction_create_form": TransactionCreateForm(
            initial={"selected_account": pk}
        ),
    }
    if pk is not None:
        selected_account = get_object_or_404(Account, pk=pk)
        context["selected_account"] = selected_account
        context["transaction_entries"] = selected_account.transactionentry_set.all()
    return render(request, "acctmgr/account_list.html", context)
