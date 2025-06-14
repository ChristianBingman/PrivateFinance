from django.shortcuts import render, reverse, HttpResponseRedirect, get_object_or_404
from django.http import HttpRequest
from .forms import CurrencyCreateForm
from .models import Currency


def currency_editor(request: HttpRequest, pk=None):
    context = {}
    if request.method == "POST":
        if pk:
            currency = get_object_or_404(Currency, pk=pk)
            form = CurrencyCreateForm(request.POST, instance=currency)
        else:
            form = CurrencyCreateForm(request.POST)
        if form.is_valid():
            form.save()
        print(form.errors)
        return HttpResponseRedirect(reverse("acctmgr:account-index"))
    if pk:
        currency = get_object_or_404(Currency, pk=pk)
        context["currency_create_form"] = CurrencyCreateForm(instance=currency)
        context["create_form_action"] = reverse(
            "currencymgr:currency-editor", args=[pk]
        )
    else:
        context["currency_create_form"] = CurrencyCreateForm()
        context["create_form_action"] = reverse("currencymgr:currency-editor")
    return render(request, "currencymgr/currency_editor.html", context)


def currency_delete(request: HttpRequest, pk: int):
    currency: Currency = get_object_or_404(Currency, pk=pk)
    currency.delete()
    return HttpResponseRedirect(reverse("acctmgr:account-index"))
