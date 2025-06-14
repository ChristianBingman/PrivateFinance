import pytest
import decimal
from .models import TransactionEntry, TransactionDetail
from .forms import TransactionCreateForm, TransactionDeleteForm
from acctmgr.models import Account
from django.db.models.deletion import RestrictedError
from datetime import datetime
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects


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


@pytest.mark.django_db
def test_simple_transaction_form(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "amount_2": decimal.Decimal("-10.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_complex_transaction_form(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A complex transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "amount_2": decimal.Decimal("-5.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
            "amount_3": decimal.Decimal("-5.00"),
            "account_3": Account.objects.get(name="Example Bank 2"),
        }
    )
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_invalid_transaction_form_with_invalid_sum(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A complex transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "amount_2": decimal.Decimal("0.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert not form.is_valid(), form.errors


@pytest.mark.django_db
def test_create_transaction_form_has_account_selected(setup_example_accounts):
    client = Client()
    res = client.get(reverse("acctmgr:account-view", args=[2]))
    assert res.context["transaction_create_form"].initial["selected_account"] == 2


@pytest.mark.django_db
def test_transaction_form_submission_redirects_on_success(setup_example_accounts):
    client = Client()
    res = client.post(
        reverse("ledger:xact-create"),
        {
            "date": "2025-05-27",
            "description": "A sample transaction",
            "amount_1": "10.00",
            "account_1": "3",
            "amount_2": "-10.00",
            "account_2": "2",
            "selected_account": 2,
        },
    )
    assertRedirects(res, reverse("acctmgr:account-view", args=[2]))


@pytest.mark.django_db
def test_transaction_form_submission_redirects_on_failure(setup_example_accounts):
    client = Client()
    res = client.post(
        reverse("ledger:xact-create"),
        {
            "date": "2025-05-27",
            "description": "A sample transaction",
            "amount_1": "10.00",
            "account_1": "100",
            "selected_account": 2,
        },
    )
    assertRedirects(res, reverse("acctmgr:account-index"))


@pytest.mark.django_db
def test_transaction_form_non_post_redirects(setup_example_accounts):
    client = Client()
    res = client.get(reverse("ledger:xact-create"))
    assertRedirects(res, reverse("acctmgr:account-index"))


@pytest.mark.django_db
def test_transaction_form_save_is_successful(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "transaction id - xxx",
            "amount_2": decimal.Decimal("-10.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert form.is_valid(), form.errors
    form.save()
    assert TransactionDetail.objects.get(pk=1).description == "A simple transaction"
    assert len(Account.objects.get(name="Dining").transactionentry_set.all()) == 1
    assert (
        len(Account.objects.get(name="Example Bank 1").transactionentry_set.all()) == 1
    )
    assert len(TransactionEntry.objects.filter(memo__startswith="transaction id")) == 1


@pytest.mark.django_db
def test_transaction_form_with_amount_and_missing_account_is_not_valid(
    setup_example_accounts,
):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A complex transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "amount_2": decimal.Decimal("-5.00"),
            "selected_account": 2,
        }
    )
    assert not form.is_valid()


@pytest.mark.django_db
def test_transaction_form_with_account_and_missing_amount_is_not_valid(
    setup_example_accounts,
):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A complex transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "account_2": Account.objects.get(name="Example Bank 1"),
            "selected_account": 2,
        }
    )
    assert not form.is_valid()


@pytest.mark.django_db
def test_transaction_form_edit_replaces_transaction_entries(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "transaction id - xxx",
            "amount_2": decimal.Decimal("-10.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert form.is_valid(), form.errors
    form.save()
    update_form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("20.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "updated transaction id - xxx",
            "amount_2": decimal.Decimal("-20.00"),
            "account_2": Account.objects.get(name="Example Bank 2"),
            "selected_transaction": 1,
        }
    )
    assert update_form.is_valid(), form.errors
    update_form.save()
    example_account_1 = Account.objects.get(name="Example Bank 1")
    example_account_2 = Account.objects.get(name="Example Bank 2")
    assert len(example_account_1.transactionentry_set.all()) == 0
    assert len(example_account_2.transactionentry_set.all()) == 1
    assert len(TransactionDetail.objects.get(pk=1).transactionentry_set.all()) == 2
    assert example_account_2.transactionentry_set.first().amount == decimal.Decimal(
        "-20.00"
    )


@pytest.mark.django_db
def test_delete_transaction_form(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "transaction id - xxx",
            "amount_2": decimal.Decimal("-10.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert form.is_valid()
    form.save()
    del_form = TransactionDeleteForm({"transaction": 1})
    assert del_form.is_valid(), del_form.errors
    assert del_form.cleaned_data["transaction"] == TransactionDetail.objects.get(pk=1)
    del_form.save()
    assert len(TransactionDetail.objects.all()) == 0


@pytest.mark.django_db
def test_delete_transaction_form_redirect_on_success(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "transaction id - xxx",
            "amount_2": decimal.Decimal("-10.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert form.is_valid()
    form.save()
    client = Client()
    res = client.post(
        reverse("ledger:xact-delete"), {"transaction": 1, "redirect_account": 1}
    )
    assertRedirects(res, reverse("acctmgr:account-view", args=[1]))


@pytest.mark.django_db
def test_delete_transaction_form_redirect_on_bad_transaction(setup_example_accounts):
    client = Client()
    res = client.post(
        reverse("ledger:xact-delete"), {"transaction": 1, "redirect_account": 1}
    )
    assertRedirects(res, reverse("acctmgr:account-index"))


@pytest.mark.django_db
def test_delete_transaction_form_redirect_on_invalid_request(setup_example_accounts):
    client = Client()
    res = client.get(reverse("ledger:xact-delete"))
    assertRedirects(res, reverse("acctmgr:account-index"))


@pytest.mark.django_db
def test_delete_transaction_form_redirect_on_missing_redirect_account(
    setup_example_accounts,
):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "transaction id - xxx",
            "amount_2": decimal.Decimal("-10.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert form.is_valid()
    form.save()
    client = Client()
    res = client.post(
        reverse("ledger:xact-delete"),
        {
            "transaction": 1,
        },
    )
    assertRedirects(res, reverse("acctmgr:account-index"))


@pytest.mark.django_db
def test_transaction_form_edit_shows_simple_transaction(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "transaction id - xxx",
            "amount_2": decimal.Decimal("-10.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
        }
    )
    assert form.is_valid()
    form.save()
    client = Client()
    res = client.get(
        reverse("acctmgr:edit-xact-view", args=[form.cleaned_data["account_1"].pk, 1])
    )
    assert res.status_code == 200
    xact_create_form_initial = res.context["transaction_create_form"].initial
    assert xact_create_form_initial["selected_transaction"] == 1
    # If it is a simple transaction, the current account should not be shown first
    assert xact_create_form_initial["account_1"] == Account.objects.get(
        name="Example Bank 1"
    )
    assert xact_create_form_initial["account_2"] == Account.objects.get(name="Dining")
    assert xact_create_form_initial["memo_1"] == "transaction id - xxx"
    assert not xact_create_form_initial.get("memo_2")


@pytest.mark.django_db
def test_transaction_form_edit_shows_complex_transaction(setup_example_accounts):
    form = TransactionCreateForm(
        {
            "date": datetime.now(),
            "description": "A simple transaction",
            "amount_1": decimal.Decimal("10.00"),
            "account_1": Account.objects.get(name="Dining"),
            "memo_2": "transaction id - xxx",
            "amount_2": decimal.Decimal("-5.00"),
            "account_2": Account.objects.get(name="Example Bank 1"),
            "amount_3": decimal.Decimal("-5.00"),
            "account_3": Account.objects.get(name="Example Bank 2"),
        }
    )
    assert form.is_valid()
    form.save()
    client = Client()
    res = client.get(
        reverse("acctmgr:edit-xact-view", args=[form.cleaned_data["account_1"].pk, 1])
    )
    assert res.status_code == 200
    xact_create_form_initial = res.context["transaction_create_form"].initial
    assert xact_create_form_initial["selected_transaction"] == 1
    assert xact_create_form_initial["account_1"] == Account.objects.get(name="Dining")
    assert xact_create_form_initial["account_2"] == Account.objects.get(
        name="Example Bank 1"
    )
    assert xact_create_form_initial["account_3"] == Account.objects.get(
        name="Example Bank 2"
    )
    assert not xact_create_form_initial.get("memo_1")
    assert xact_create_form_initial["memo_2"] == "transaction id - xxx"
    assert not xact_create_form_initial.get("memo_3")
    assert xact_create_form_initial["amount_1"] == decimal.Decimal("10.00")
    assert xact_create_form_initial["amount_2"] == decimal.Decimal("-5.00")
    assert xact_create_form_initial["amount_3"] == decimal.Decimal("-5.00")


def test_transaction_create_default_reverse_entry_with_different_currency(): ...


def test_transaction_create_form_with_new_account():
    # Ensure that a fresh account still shows the transaction create form
    ...


def test_transaction_create_form_auto_balances():
    # Will need selenium for this
    ...


def test_transaction_create_form_with_different_prices_balances():
    # Will need selenium for this
    ...
