from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest

from .models import Account
from ledger.models import TransactionDetail
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
        context["transaction_entries"] = (
            selected_account.transactionentry_set.all().order_by(
                "transaction_id__xact_date"
            )
        )
    return render(request, "acctmgr/account_list.html", context)


def edit(request: HttpRequest, account_pk, transactiondetail_pk):
    transaction_to_edit = get_object_or_404(TransactionDetail, pk=transactiondetail_pk)
    selected_account = get_object_or_404(Account, pk=account_pk)
    initial = {
        "date": transaction_to_edit.xact_date,
        "description": transaction_to_edit.description,
        "selected_transaction": transactiondetail_pk,
        "selected_account": account_pk,
    }
    transaction_entries = transaction_to_edit.transactionentry_set.all()
    if len(transaction_entries) == 2:
        transaction_entries = filter(
            lambda entry: entry.account != selected_account, transaction_entries
        )
    current_entry = 1
    for xact_entry in transaction_entries:
        initial[f"memo_{current_entry}"] = xact_entry.memo
        initial[f"account_{current_entry}"] = xact_entry.account
        initial[f"amount_{current_entry}"] = xact_entry.amount
        current_entry += 1
    context = {
        "accounts": Account.objects.get_accounts(),
        "transaction_create_form": TransactionCreateForm(initial=initial),
    }
    context["selected_account"] = selected_account
    context["transaction_entries"] = (
        selected_account.transactionentry_set.all().order_by(
            "transaction_id__xact_date"
        )
    )
    return render(request, "acctmgr/account_list.html", context)
