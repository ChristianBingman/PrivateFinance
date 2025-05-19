from django.db import models
from datetime import datetime
from acctmgr.models import Account, Currency

class TransactionDetail(models.Model):
    id = models.BigAutoField("transaction id", primary_key=True)
    description = models.CharField(max_length=100)
    xact_date = models.DateField(default=datetime.now)

class Transaction(models.Model):
    # Deleting the transaction detail should delete all entries for that xact
    transaction_id = models.ForeignKey(TransactionDetail, on_delete=models.CASCADE)
    # Deleting the account without explicitly deleting all transactions is restricted
    account = models.ForeignKey(Account, on_delete=models.RESTRICT)
    memo = models.CharField(max_length=256)
    price = models.DecimalField(decimal_places=10, max_digits=19, default=1.0)
    amount = models.DecimalField(decimal_places=10, max_digits=19)
