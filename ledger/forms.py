from django import forms
import datetime
import decimal
from functools import reduce
from acctmgr.models import Account
from django.core.exceptions import ValidationError


class TransactionCreateForm(forms.Form):
    template_name = "ledger/xact_create_form_template.html"
    date = forms.DateField(initial=datetime.datetime.now())
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
            self.fields[f"account_{i}"] = forms.ModelChoiceField(
                accounts,
                required=True if i == 1 else False,
                widget=forms.widgets.Select(
                    attrs={"hidden": False if i == 1 else True}
                ),
            )

    def clean(self):
        transaction_tuples: list[tuple[str | None, decimal.Decimal, Account]] = []
        cleaned_data_iter = iter(self.cleaned_data.values())
        # skip date, description and selected account
        next(cleaned_data_iter)
        next(cleaned_data_iter)
        selected_account = next(cleaned_data_iter)
        memo = next(cleaned_data_iter)
        amount = next(cleaned_data_iter)
        while account := next(cleaned_data_iter):
            transaction_tuples.append((memo, amount, account))
            memo = next(cleaned_data_iter)
            amount = next(cleaned_data_iter)

        # If it is a simple transaction, add the reverse entry
        if len(transaction_tuples) == 1:
            # TODO: Make sure this get is safe
            transaction_tuples.append(
                (
                    "",
                    -transaction_tuples[0][1],
                    Account.objects.get(pk=selected_account),
                )
            )

        self.cleaned_data["transactions"] = transaction_tuples

        # TODO: Handle potentially bad input
        xact_sum = reduce(lambda acc, val: acc + val[1], transaction_tuples, 0)
        if xact_sum != 0:
            # In the future we should just throw the difference in an imbalance account
            raise ValidationError("Transaction does not sum to 0.")
        return self.cleaned_data
