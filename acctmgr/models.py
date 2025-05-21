from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from functools import reduce
from decimal import Decimal, ROUND_HALF_DOWN
import operator


class Currency(models.Model):
    """A currency used to define the value of an account and the currency traded in a transaction"""

    full_name = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10, unique=True)
    # Allows for 10 Quadrillion with 2 Decimal Places or 100 Million with 10 Decimal Places
    current_price = models.DecimalField(decimal_places=10, max_digits=19, default=1)
    # Smallest fraction traded for the currency
    fraction_traded = models.PositiveIntegerField(default=2)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.full_name == "":
            self.full_name = self.symbol
        self.current_price = Decimal(self.current_price).quantize(Decimal(str(1.0/(10**self.fraction_traded))), rounding=ROUND_HALF_DOWN)
        super().save(*args,**kwargs)


class AccountTypes(models.TextChoices):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AccountManager(models.Manager):
    def _build_account_tree(self, account: "Account"):
        children = account.account_set.all()
        if len(children) == 0:
            return {account: []}

        return {account: [self._build_account_tree(account) for account in children]}

    def get_accounts(self) -> dict:
        """Get a list of accounts structured

        Returns:
        {"asset": QuerySet, "liability": QuerySet, "equity": QuerySet, "revenue": QuerySet, "expense": QuerySet}
        """
        types = [
            {acct_type: [self._build_account_tree(account) for account in self.get_accounts_by_type(acct_type).filter(parent=None)]}
            for acct_type in AccountTypes
        ]
        return dict(reduce(operator.or_, types, {}))


class AccountQuerySet(models.QuerySet):
    def get_accounts_by_type(self, account_type: AccountTypes) -> models.QuerySet:
        return self.filter(acct_type=account_type)


class Account(models.Model):
    """An account which can be used to transfer value to and from"""

    name = models.CharField(max_length=20)
    # Protect the Currency, we don't want to delete accounts when
    # a currency is deleted, accounts should be deleted first
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    acct_type = models.CharField(max_length=10, choices=AccountTypes)
    # Additional account information
    description = models.CharField(max_length=100)
    parent = models.ForeignKey("Account", null=True, on_delete=models.CASCADE)
    placeholder = models.BooleanField(default=False)
    objects = AccountManager.from_queryset(AccountQuerySet)()

    def __str__(self):
        return self.name

    def clean(self):
        current = self.parent
        while current != None:
            if current.pk == self.pk:
                raise ValidationError("Detected cycle when setting parent.")
            current = current.parent
