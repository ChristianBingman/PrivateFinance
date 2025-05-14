import pytest
from decimal import Decimal

from .models import Currency, CurrencyForm, Account, AccountTypes


@pytest.mark.django_db
def test_create_simple_currency():
    usd_cur = Currency(
        full_name="USD", symbol="USD", current_price=1.0, fraction_traded=2
    )
    usd_cur.save()
    assert len(Currency.objects.all()) == 1


@pytest.mark.django_db
def test_invalid_fraction_traded():
    with pytest.raises(ValueError):
        inv_cur = {
            "full_name": "Invalid Currency",
            "symbol": "INV",
            "current_price": 1.1234,
            "fraction_traded": 2,
        }
        curr_form = CurrencyForm(inv_cur)
        assert not curr_form.is_valid()
        curr_form.save()


@pytest.mark.django_db
def test_only_required_attribute():
    currency = CurrencyForm({"full_name": "USD", "symbol": "USD"})
    currency.save()
    usd_cur = Currency.objects.get(symbol="USD")
    assert usd_cur.full_name == "USD"
    assert usd_cur.symbol == "USD"
    assert usd_cur.fraction_traded == 2
    assert usd_cur.current_price == Decimal(1.0)


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


@pytest.mark.django_db
def test_get_account_listing(setup_example_db):
    accounts = Account.objects.get_accounts()
    assert list(accounts.keys()) == list(AccountTypes)
    for acct_type in AccountTypes:
        assert list(Account.objects.filter(acct_type=acct_type)) == list(
            accounts[acct_type]
        )
