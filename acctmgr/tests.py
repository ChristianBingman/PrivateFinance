import pytest
from functools import reduce
import operator
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import Client
from django.shortcuts import reverse
from pytest_django.asserts import assertRedirects

from .models import Currency, Account, AccountTypes


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
def test_get_account_listing(setup_example_accounts):
    accounts = Account.objects.get_accounts()
    assert list(accounts.keys()) == list(AccountTypes)
    for account in accounts.values():
        validate_child(account)


@pytest.mark.django_db
def test_cycles_not_allowed(setup_example_accounts):
    savings_account = Account.objects.get(description__contains="Savings Account")
    parent_account = Account.objects.get(name="Bank Accounts")
    parent_account.parent = savings_account
    with pytest.raises(ValidationError):
        parent_account.full_clean()


@pytest.mark.django_db
def test_duplicate_currencies(setup_example_accounts):
    dup_cur = Currency(full_name="New currency", symbol="USD")
    with pytest.raises(IntegrityError):
        dup_cur.save()


@pytest.mark.django_db
def test_account_create_success():
    usd_cur = Currency.objects.create(symbol="USD")
    client = Client()
    res = client.post(
        reverse("acctmgr:account-editor"),
        {
            "name": "Bank Account 1",
            "currency": "1",
            "acct_type": AccountTypes.ASSET,
            "description": "Test Account",
        },
    )
    assertRedirects(res, reverse("acctmgr:account-index"))
    account = Account.objects.get(pk=1)
    assert account is not None
    assert account.name == "Bank Account 1"
    assert account.currency == usd_cur
    assert account.acct_type == AccountTypes.ASSET
    assert account.description == "Test Account"
    assert not account.placeholder


@pytest.mark.django_db
def test_account_create_invalid_form():
    client = Client()
    res = client.post(reverse("acctmgr:account-editor"), {})
    assertRedirects(res, reverse("acctmgr:account-index"))


@pytest.mark.django_db
def test_account_form_displayed_on_account_editor():
    client = Client()
    res = client.get(reverse("acctmgr:account-editor"))
    assert res.context["account_create_form"]
    assert f'action="{reverse("acctmgr:account-editor")}"' in str(res.content)


@pytest.mark.django_db
def test_account_edit_success(setup_example_accounts):
    client = Client()
    res = client.get(reverse("acctmgr:account-editor", args=[2]))
    acct_form_initial = res.context["account_create_form"].initial
    assert acct_form_initial["name"] == "Example Bank 1"
    assert acct_form_initial["currency"] == Currency.objects.get(symbol="USD").pk
    assert acct_form_initial["acct_type"] == AccountTypes.ASSET
    assert acct_form_initial["description"] == "Primary Checking Account"
    assert acct_form_initial["parent"] == 1
    assert acct_form_initial["placeholder"] is False
    acct_form_initial["description"] = "Old Checking Account"
    res = client.post(reverse("acctmgr:account-editor", args=[2]), acct_form_initial)
    assertRedirects(res, reverse("acctmgr:account-index"))
    assert Account.objects.get(pk=2).description == "Old Checking Account"


@pytest.mark.django_db
def test_account_delete_success(setup_example_accounts):
    client = Client()
    res = client.get(reverse("acctmgr:account-delete", args=[2]))
    assertRedirects(res, reverse("acctmgr:account-index"))
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.get(pk=2)
