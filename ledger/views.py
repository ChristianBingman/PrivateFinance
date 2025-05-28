from django.http import HttpResponseRedirect, HttpRequest
from django.urls import reverse
from .forms import TransactionCreateForm


# Create your views here.
def xact_create(request: HttpRequest):
    print(request.GET)
    if request.method == "POST":
        form = TransactionCreateForm(request.POST)
        if form.is_valid():
            # TODO: Create the data
            return HttpResponseRedirect(
                reverse(
                    "acctmgr:account-view", args=[form.cleaned_data["selected_account"]]
                )
            )
    return HttpResponseRedirect(reverse("acctmgr:account-index"))
