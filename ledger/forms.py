from django import forms
import datetime
import decimal
from functools import reduce
from acctmgr.models import Account
from django.core.exceptions import ValidationError
from .models import TransactionDetail, TransactionEntry
from django.db import transaction


class TransactionDeleteForm(forms.Form):
    transaction = forms.IntegerField(min_value=1, widget=forms.widgets.HiddenInput())

    # The account we want to redirect back to if valid
    redirect_account = forms.IntegerField(
        required=False, min_value=1, widget=forms.widgets.HiddenInput()
    )

    def clean_transaction(self):
        try:
            xact = TransactionDetail.objects.get(pk=self.cleaned_data["transaction"])
            return xact
        except TransactionDetail.DoesNotExist:
            raise ValidationError("Invalid transaction id")

    def save(self):
        self.cleaned_data["transaction"].delete()


class TransactionCreateForm(forms.Form):
    template_name = "ledger/xact_create_form_template.html"
    date = forms.DateField(initial=datetime.datetime.now(), required=True)
    description = forms.CharField(
        required=True,
        max_length=256,
        widget=forms.widgets.TextInput(
            attrs={"placeholder": "Transaction Description"}
        ),
    )
    selected_account = forms.IntegerField(
        required=False, widget=forms.widgets.NumberInput(attrs={"hidden": True})
    )
    selected_transaction = forms.IntegerField(
        required=False, widget=forms.widgets.HiddenInput()
    )
    max_split = 20

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        accounts = Account.objects.filter(placeholder=False)
        for i in range(1, self.max_split + 1):
            self.fields[f"memo_{i}"] = forms.CharField(
                required=False,
                max_length=256,
                widget=forms.widgets.TextInput(
                    attrs={"placeholder": "memo", "hidden": True}
                ),
            )
            self.fields[f"amount_{i}"] = forms.DecimalField(
                required=True if i == 1 else False,
                max_digits=19,
                decimal_places=10,
                widget=forms.widgets.NumberInput(
                    attrs={"hidden": False if i == 1 else True}
                ),
            )
            self.fields[f"price_{i}"] = forms.DecimalField(
                required=False,
                max_digits=19,
                decimal_places=10,
                widget=forms.widgets.NumberInput(
                    attrs={"placeholder": "price", "hidden": True}
                ),
            )
            self.fields[f"account_{i}"] = forms.ModelChoiceField(
                accounts,
                required=True if i == 1 else False,
                widget=forms.widgets.Select(
                    attrs={"hidden": False if i == 1 else True}
                ),
            )

    def clean(self, *args, **kwargs):
        transaction_tuples: list[
            tuple[str | None, decimal.Decimal, decimal.Decimal, Account]
        ] = []
        for i in range(1, self.max_split):
            memo = self.cleaned_data.get(f"memo_{i}", None)
            account = self.cleaned_data.get(f"account_{i}", None)
            amount = self.cleaned_data.get(f"amount_{i}", None)
            price = self.cleaned_data.get(f"price_{i}", None)
            if account is not None and amount is None:
                raise ValidationError("Amount is required when account is defined")
            elif account is None and amount is not None:
                raise ValidationError("Account is required when amount is defined")
            elif account is not None and amount is not None:
                if price is None:
                    price = account.currency.current_price
                transaction_tuples.append((memo, amount, price, account))

        self.cleaned_data["transactions"] = transaction_tuples

        xact_sum = reduce(lambda acc, val: acc + val[1] * val[2], transaction_tuples, 0)
        if xact_sum != 0:
            # In the future we should just throw the difference in an imbalance account
            raise ValidationError("Transaction does not sum to 0.")
        return self.cleaned_data

    @transaction.atomic
    def save(self):
        """Saves the form, including transactions

        Raises:
        ValueError -- Transaction is not balanced
        """
        if self.cleaned_data["selected_transaction"]:
            xact_detail = TransactionDetail.objects.get(
                pk=self.cleaned_data["selected_transaction"]
            )
            xact_detail.xact_date = self.cleaned_data["date"]
            xact_detail.description = self.cleaned_data["description"]
            # Delete the entries since we will revalidate and recreate them
            # If transactions are edited often then another solution would
            # be to only recreate the ones that are modified, or even better
            # just reuse as many as we can, but that gets more complicated
            TransactionEntry.objects.filter(transaction_id=xact_detail).delete()
        else:
            xact_detail = TransactionDetail(
                description=self.cleaned_data["description"],
                xact_date=self.cleaned_data["date"],
            )
        xact_detail.save()
        entries = []
        for memo, amount, price, account in self.cleaned_data["transactions"]:
            entries.append(
                TransactionEntry(
                    transaction_id=xact_detail,
                    account=account,
                    memo=memo,
                    amount=amount,
                    price=price,
                )
            )
        TransactionEntry.objects.create_balanced_transaction(entries)
