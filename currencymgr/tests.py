import pytest
from .models import Currency
from decimal import Decimal
from django.test import Client
from django.shortcuts import reverse
from pytest_django.asserts import assertRedirects


@pytest.fixture
def create_sample_currencies():
    Currency.objects.create(
        full_name="United States Dollar",
        symbol="USD",
        current_price=Decimal("1.0"),
        fraction_traded=2,
    )
    Currency.objects.create(
        full_name="Some Stock",
        symbol="STK",
        current_price=Decimal("123.45"),
        fraction_traded=8,
    )


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
def test_currency_create_success():
    client = Client()
    res = client.post(
        reverse("currencymgr:currency-editor"),
        {
            "full_name": "United States Dollar",
            "symbol": "USD",
            "current_price": "1",
            "fraction_traded": 2,
        },
    )
    assertRedirects(res, reverse("acctmgr:account-index"))
    currency = Currency.objects.get(pk=1)
    assert currency is not None
    assert currency.symbol == "USD"
    assert currency.full_name == "United States Dollar"
    assert currency.fraction_traded == 2
    assert currency.current_price == Decimal("1")


@pytest.mark.django_db
def test_currency_create_invalid_form():
    client = Client()
    res = client.post(reverse("currencymgr:currency-editor"), {})
    assertRedirects(res, reverse("acctmgr:account-index"))


@pytest.mark.django_db
def test_currency_form_displayed_on_currency_editor():
    client = Client()
    res = client.get(reverse("currencymgr:currency-editor"))
    assert res.context["currency_create_form"]
    assert f'action="{reverse("currencymgr:currency-editor")}"' in str(res.content)


@pytest.mark.django_db
def test_curency_edit_success(create_sample_currencies):
    client = Client()
    res = client.get(reverse("currencymgr:currency-editor", args=[1]))
    cur_form_initial = res.context["currency_create_form"].initial
    assert cur_form_initial["current_price"] == Decimal("1")
    assert cur_form_initial["fraction_traded"] == 2
    assert cur_form_initial["symbol"] == "USD"
    assert cur_form_initial["full_name"] == "United States Dollar"
    cur_form_initial["symbol"] = "USA"
    res = client.post(
        reverse("currencymgr:currency-editor", args=[1]), cur_form_initial
    )
    assertRedirects(res, reverse("acctmgr:account-index"))
    assert Currency.objects.get(pk=1).symbol == "USA"


@pytest.mark.django_db
def test_currency_delete_success(create_sample_currencies):
    client = Client()
    res = client.get(reverse("currencymgr:currency-delete", args=[1]))
    assertRedirects(res, reverse("acctmgr:account-index"))
    with pytest.raises(Currency.DoesNotExist):
        Currency.objects.get(pk=1)
