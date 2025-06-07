from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.urls import reverse
from .forms import TransactionCreateForm, TransactionDeleteForm


def xact_create(request: HttpRequest):
    if request.method == "POST":
        form = TransactionCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse(
                    "acctmgr:account-view", args=[form.cleaned_data["selected_account"]]
                )
            )
        else:
            print(form.errors)
    return HttpResponseRedirect(reverse("acctmgr:account-index"))


def xact_delete(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        print(request.POST)
        form = TransactionDeleteForm(request.POST)
        if form.is_valid():
            form.save()
            if redirect_account := form.cleaned_data["redirect_account"]:
                return HttpResponseRedirect(
                    reverse("acctmgr:account-view", args=[redirect_account])
                )
        else:
            print(form.errors)
    return HttpResponseRedirect(reverse("acctmgr:account-index"))
