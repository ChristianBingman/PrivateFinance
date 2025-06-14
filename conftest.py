from currencymgr.models import Currency
from acctmgr.models import Account, AccountTypes
import pytest


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
        description="Primary Checking Account",
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
