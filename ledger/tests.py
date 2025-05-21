import pytest
import decimal
from .models import TransactionEntry, TransactionDetail
from acctmgr.models import Account, Currency, AccountTypes
from django.db.models.deletion import RestrictedError
from datetime import datetime


@pytest.fixture
def setup_example_accounts():
    usd_cur = Currency(
        full_name="USD", symbol="USD", current_price=1.0, fraction_traded=2
    )
    usd_cur.save()
    bank_accounts_placeholder = Account(
        name="Bank Accounts",
        currency=usd_cur,
        acct_type="asset",
        description="My Checking Accounts",
        placeholder=True,
    )
    bank_accounts_placeholder.save()
    Account(
        name="Example Bank 1",
        currency=usd_cur,
        acct_type=AccountTypes.ASSET,
        description="Primary Checkng Account",
        parent=bank_accounts_placeholder,
    ).save()
    Account(
        name="Example Bank 2",
        currency=usd_cur,
        acct_type=AccountTypes.ASSET,
        description="Primary Savings Account",
        parent=bank_accounts_placeholder,
    ).save()
    Account(
        name="Dining",
        currency=usd_cur,
        acct_type=AccountTypes.EXPENSE,
        description="Dining Expenses",
    ).save()
    sample_liabilities_account = Account(
        name="Student Loans",
        currency=usd_cur,
        acct_type=AccountTypes.LIABILITY,
        description="American Student Loans",
        placeholder=True,
    )
    sample_liabilities_account.save()
    Account(
        name="Loan A",
        currency=usd_cur,
        acct_type=AccountTypes.LIABILITY,
        description="Loan Account A",
        parent=sample_liabilities_account,
    ).save()
    Account(
        name="Loan B",
        currency=usd_cur,
        acct_type=AccountTypes.LIABILITY,
        description="Loan Account B",
        parent=sample_liabilities_account,
    ).save()
    Account(
        name="Salary",
        currency=usd_cur,
        acct_type=AccountTypes.REVENUE,
        description="Work Salary",
    ).save()
    Account(
        name="Other Income",
        currency=usd_cur,
        acct_type=AccountTypes.REVENUE,
        description="Extra Income",
    ).save()
    Account(
        name="Opening Balances",
        currency=usd_cur,
        acct_type=AccountTypes.EQUITY,
        description="Opening Balances",
    ).save()


@pytest.mark.django_db
def test_create_transaction(setup_example_accounts):
    # A double and many entry transaction should create
    xact_detail = TransactionDetail(
        description="A Sample Transaction", xact_date=datetime.now()
    )
    xact_detail.save()
    from_account = Account.objects.get(name="Salary")
    to_account = Account.objects.get(name="Example Bank 1")

    entry1 = TransactionEntry(
        transaction_id=xact_detail,
        account=from_account,
        amount=decimal.Decimal("-10.00"),
    )
    entry2 = TransactionEntry(
        transaction_id=xact_detail, account=to_account, amount=decimal.Decimal("10.00")
    )

    TransactionEntry.objects.create_balanced_transaction([entry1, entry2])

    assert len(xact_detail.transactionentry_set.all()) == 2


@pytest.mark.django_db
def test_create_transaction_with_extra_precision(setup_example_accounts):
    # Amounts that don't abide by the fraction traded should be rounded
    xact_detail = TransactionDetail(
        description="A Sample Transaction", xact_date=datetime.now()
    )
    xact_detail.save()
    from_account = Account.objects.get(name="Salary")

    # The salary account only has 2 decimal places
    entry1 = TransactionEntry.objects.create(
        transaction_id=xact_detail,
        account=from_account,
        amount=decimal.Decimal("-10.001"),
    )
    assert entry1.amount == decimal.Decimal("-10.00")


@pytest.mark.django_db
def test_invalid_transaction_amount(setup_example_accounts):
    # A double and many entry transaction should create
    xact_detail = TransactionDetail(
        description="A Sample Transaction", xact_date=datetime.now()
    )
    xact_detail.save()
    from_account = Account.objects.get(name="Salary")
    to_account = Account.objects.get(name="Example Bank 1")

    entry1 = TransactionEntry(
        transaction_id=xact_detail,
        account=from_account,
        amount=decimal.Decimal("-10.00"),
    )
    entry2 = TransactionEntry(
        transaction_id=xact_detail, account=to_account, amount=decimal.Decimal("1.00")
    )
    with pytest.raises(ValueError):
        TransactionEntry.objects.create_balanced_transaction([entry1, entry2])
    assert len(xact_detail.transactionentry_set.all()) == 0


@pytest.mark.django_db
def test_default_transaction_values(setup_example_accounts):
    # Test the default values for transaction and transaction details
    # Amounts that don't abide by the fraction traded should be rounded
    xact_detail = TransactionDetail(
        description="A Sample Transaction", xact_date=datetime.now()
    )
    xact_detail.save()
    from_account = Account.objects.get(name="Salary")

    # The salary account only has 2 decimal places
    entry1 = TransactionEntry.objects.create(
        transaction_id=xact_detail,
        account=from_account,
        amount=decimal.Decimal("-10.001"),
    )
    assert entry1.price == decimal.Decimal(1)
    assert entry1.memo == ""


@pytest.mark.django_db
def test_create_entries_multiple_accounts(setup_example_accounts):
    # Check that create_balanced_transaction doesn't accept multiple transactions
    xact_detail = TransactionDetail(
        description="A Sample Transaction", xact_date=datetime.now()
    )
    xact_detail_2 = TransactionDetail(
        description="A Different Transaction", xact_date=datetime.now()
    )
    xact_detail.save()

    from_account = Account.objects.get(name="Salary")
    to_account = Account.objects.get(name="Example Bank 1")

    entry1 = TransactionEntry(
        transaction_id=xact_detail,
        account=from_account,
        amount=decimal.Decimal("-10.00"),
    )
    entry2 = TransactionEntry(
        transaction_id=xact_detail_2,
        account=to_account,
        amount=decimal.Decimal("10.00"),
    )
    with pytest.raises(ValueError):
        TransactionEntry.objects.create_balanced_transaction([entry1, entry2])


@pytest.mark.django_db
def test_account_deletion_restricted(setup_example_accounts):
    # Deleting an account without also deleting the entries should be restricted
    xact_detail = TransactionDetail(
        description="A Sample Transaction", xact_date=datetime.now()
    )
    xact_detail.save()
    from_account = Account.objects.get(name="Salary")
    to_account = Account.objects.get(name="Example Bank 1")

    entry1 = TransactionEntry(
        transaction_id=xact_detail,
        account=from_account,
        amount=decimal.Decimal("-10.00"),
    )
    entry2 = TransactionEntry(
        transaction_id=xact_detail, account=to_account, amount=decimal.Decimal("10.00")
    )

    TransactionEntry.objects.create_balanced_transaction([entry1, entry2])

    with pytest.raises(RestrictedError):
        from_account.delete()


@pytest.mark.django_db
def test_account_transaction_query(setup_example_accounts):
    # Test querying all transactions by account
    xact_detail = TransactionDetail(
        description="A Sample Transaction", xact_date=datetime.now()
    )
    xact_detail.save()
    from_account = Account.objects.get(name="Salary")
    to_account = Account.objects.get(name="Example Bank 1")

    entry1 = TransactionEntry(
        transaction_id=xact_detail,
        account=from_account,
        amount=decimal.Decimal("-10.00"),
    )
    entry2 = TransactionEntry(
        transaction_id=xact_detail, account=to_account, amount=decimal.Decimal("10.00")
    )

    TransactionEntry.objects.create_balanced_transaction([entry1, entry2])

    assert len(from_account.transactionentry_set.all()) == 1
    assert len(to_account.transactionentry_set.all()) == 1
