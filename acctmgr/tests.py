import pytest
from decimal import Decimal
from functools import reduce
import operator
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from .models import Currency, Account, AccountTypes


@pytest.mark.django_db
def test_create_simple_currency():
    usd_cur = Currency(
        full_name="USD", symbol="USD", current_price=1, fraction_traded=2
    )
    usd_cur.save()
    assert len(Currency.objects.all()) == 1


@pytest.mark.django_db
def test_rounding_price():
    Currency.objects.create(
        full_name="Rounded Currency",
        symbol="RND",
        current_price=Decimal("1.1234"),
        fraction_traded=2,
    )
    assert Currency.objects.get(symbol="RND").current_price == Decimal("1.12")


@pytest.mark.django_db
def test_only_required_attribute():
    usd_cur = Currency.objects.create(symbol="USD")
    assert str(usd_cur) == "USD"
    assert usd_cur.symbol == "USD"
    assert usd_cur.fraction_traded == 2
    assert usd_cur.current_price == Decimal(1.00)


@pytest.mark.django_db
def test_create_simple_account():
    usd_cur = Currency(
        full_name="USD", symbol="USD", current_price=1.0, fraction_traded=2
    )
    usd_cur.save()
    sample_account = Account(
        name="Some Bank",
        currency=usd_cur,
        acct_type="asset",
        description="My Checking Account",
    )
    sample_account.save()
    assert Account.objects.count() == 1
    assert str(sample_account) == "Some Bank"


@pytest.mark.django_db
def test_create_child_account():
    usd_cur = Currency(
        full_name="USD", symbol="USD", current_price=1.0, fraction_traded=2
    )
    usd_cur.save()
    sample_account = Account(
        name="Bank Accounts",
        currency=usd_cur,
        acct_type="asset",
        description="My Checking Accounts",
        placeholder=True,
    )
    sample_account.save()
    child_account = Account(
        name="Chase Bank",
        currency=usd_cur,
        acct_type=AccountTypes.ASSET,
        description="Primary Checkng Account",
        parent=sample_account,
    )
    child_account.save()
    assert len(sample_account.account_set.all()) == 1
    assert not child_account.placeholder


@pytest.fixture
def setup_example_db():
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
        name="Example Bank",
        currency=usd_cur,
        acct_type=AccountTypes.ASSET,
        description="Primary Checkng Account",
        parent=bank_accounts_placeholder,
    ).save()
    Account(
        name="Example Bank",
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


def validate_child(accounts: list[dict]):
    # if there are children check they are valid first
    # then check that the children are the same
    for account in accounts:
        for parent, children in account.items():
            validate_child(children)
            children_qs = parent.account_set.all()
            if len(children) == 0:
                assert len(children_qs) == 0
            else:
                assert list(children_qs) == list(reduce(operator.or_, children).keys())


@pytest.mark.django_db
def test_get_account_listing(setup_example_db):
    accounts = Account.objects.get_accounts()
    assert list(accounts.keys()) == list(AccountTypes)
    for account in accounts.values():
        validate_child(account)


@pytest.mark.django_db
def test_cycles_not_allowed(setup_example_db):
    savings_account = Account.objects.get(description__contains="Savings Account")
    parent_account = Account.objects.get(name="Bank Accounts")
    parent_account.parent = savings_account
    with pytest.raises(ValidationError):
        parent_account.full_clean()


@pytest.mark.django_db
def test_duplicate_currencies(setup_example_db):
    dup_cur = Currency(full_name="New currency", symbol="USD")
    with pytest.raises(IntegrityError):
        dup_cur.save()
