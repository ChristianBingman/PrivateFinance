from django.db import models
from django.core.exceptions import ValidationError
from functools import reduce
import operator
from currencymgr.models import Currency


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
            {
                acct_type: [
                    self._build_account_tree(account)
                    for account in self.get_accounts_by_type(acct_type).filter(
                        parent=None
                    )
                ]
            }
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
    parent = models.ForeignKey(
        "Account", blank=True, null=True, on_delete=models.CASCADE
    )
    placeholder = models.BooleanField(default=False)
    objects = AccountManager.from_queryset(AccountQuerySet)()

    def __str__(self):
        return self.name

    def validate_no_cycle(self):
        current = self.parent
        while current is not None:
            if current.pk == self.pk:
                raise ValidationError("Detected cycle when setting parent.")
            current = current.parent

    def clean(self, *args, **kwargs):
        self.validate_no_cycle()
        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
