from django.db import models
from decimal import Decimal, ROUND_HALF_DOWN


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
        self.current_price = Decimal(self.current_price).quantize(
            Decimal(str(1.0 / (10**self.fraction_traded))), rounding=ROUND_HALF_DOWN
        )
        super().save(*args, **kwargs)
