from django.db import models, transaction
from datetime import datetime
from acctmgr.models import Account
import decimal


class TransactionDetail(models.Model):
    id = models.BigAutoField("transaction id", primary_key=True)
    description = models.CharField(max_length=100)
    xact_date = models.DateField(default=datetime.now)


class TransactionManager(models.Manager):
    @transaction.atomic
    def create_balanced_transaction(self, entries: list["TransactionEntry"]):
        transaction_id = entries[0].transaction_id
        for entry in entries:
            if entry.transaction_id != transaction_id:
                raise ValueError("All entries must have the same transaction id.")
            entry.save()

        total = decimal.Decimal(0)
        for xact in self.filter(transaction_id=transaction_id):
            total += decimal.Decimal(xact.amount)
        if total != decimal.Decimal(0):
            raise ValueError("Transaction is not balanced.")


class TransactionEntry(models.Model):
    # Deleting the transaction detail should delete all entries for that xact
    transaction_id = models.ForeignKey(TransactionDetail, on_delete=models.CASCADE)
    # Deleting the account without explicitly deleting all transactions is restricted
    account = models.ForeignKey(Account, on_delete=models.RESTRICT)
    memo = models.CharField(max_length=256, blank=True)
    price = models.DecimalField(decimal_places=10, max_digits=19, default=1)
    amount = models.DecimalField(decimal_places=10, max_digits=19)
    objects = TransactionManager()

    def save(self, *args, **kwargs):
        self.amount = decimal.Decimal(self.amount).quantize(
            decimal.Decimal(str(1.0 / (10**self.account.currency.fraction_traded))),
            rounding=decimal.ROUND_HALF_DOWN,
        )
        self.price = decimal.Decimal(self.price).quantize(
            decimal.Decimal(str(1.0 / (10**self.account.currency.fraction_traded))),
            rounding=decimal.ROUND_HALF_DOWN,
        )
        super().save(*args, **kwargs)
