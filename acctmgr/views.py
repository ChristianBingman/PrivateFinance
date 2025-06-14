from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpRequest, HttpResponseRedirect
from django.db.models import QuerySet
import decimal

from .models import Account
from ledger.models import TransactionDetail, TransactionEntry
from ledger.forms import TransactionCreateForm, TransactionDeleteForm
import acctmgr.forms


def index(request: HttpRequest, pk=None, transaction_pk=None):
    context = {}
    if pk is not None:
        transaction_form_initial = {"selected_account": pk}
        selected_account = get_object_or_404(Account, pk=pk)
        if transaction_pk is not None:
            transaction_to_edit = get_object_or_404(
                TransactionDetail, pk=transaction_pk
            )
            transaction_form_initial.update(
                {
                    "date": transaction_to_edit.xact_date,
                    "description": transaction_to_edit.description,
                    "selected_transaction": transaction_to_edit.id,
                }
            )
            transaction_entries: QuerySet = (
                transaction_to_edit.transactionentry_set.all().order_by("pk")
            )
            if (
                len(transaction_entries) == 2
                and transaction_entries[0].account.pk == pk
            ):
                transaction_entries = [transaction_entries[1], transaction_entries[0]]
            current_entry = 1
            for xact_entry in transaction_entries:
                transaction_form_initial[f"memo_{current_entry}"] = xact_entry.memo
                transaction_form_initial[f"account_{current_entry}"] = (
                    xact_entry.account
                )
                transaction_form_initial[f"price_{current_entry}"] = xact_entry.price
                transaction_form_initial[f"amount_{current_entry}"] = (
                    xact_entry.amount.quantize(
                        decimal.Decimal(
                            "1." + "0" * xact_entry.account.currency.fraction_traded
                        )
                    )
                )
                current_entry += 1
            context["transaction_delete_form"] = TransactionDeleteForm(
                {
                    "transaction": transaction_pk,
                    "redirect_account": pk,
                }
            )
        context["transaction_create_form"] = TransactionCreateForm(
            initial=transaction_form_initial
        )
        context["selected_account"] = selected_account
        context["transaction_entries"] = TransactionEntry.objects.filter(
            account=selected_account
        ).order_by("transaction_id__xact_date")
    return render(request, "acctmgr/account_list.html", context)


def account_editor(request: HttpRequest, pk=None):
    context = {}
    if request.method == "POST":
        if pk:
            account = get_object_or_404(Account, pk=pk)
            form = acctmgr.forms.AccountCreateForm(request.POST, instance=account)
        else:
            form = acctmgr.forms.AccountCreateForm(request.POST)
        if form.is_valid():
            form.save()
        print(form.errors)
        return HttpResponseRedirect(reverse("acctmgr:account-index"))
    if pk:
        account = get_object_or_404(Account, pk=pk)
        context["account_create_form"] = acctmgr.forms.AccountCreateForm(
            instance=account
        )
        context["create_form_action"] = reverse("acctmgr:account-editor", args=[pk])
    else:
        context["account_create_form"] = acctmgr.forms.AccountCreateForm()
        context["create_form_action"] = reverse("acctmgr:account-editor")
    return render(request, "acctmgr/account_editor.html", context)


def account_delete(request: HttpRequest, pk: int):
    account: Account = get_object_or_404(Account, pk=pk)
    account.delete()
    return HttpResponseRedirect(reverse("acctmgr:account-index"))
