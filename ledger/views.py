from django.http import HttpResponse
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from acctmgr.models import Account


# Create your views here.
def index(request):
    return HttpResponse("This will display the list of transactions for an account.")


class AccountView(ListView):
    template_name = "ledger/account_entry_list.html"

    def get_queryset(self):
        account = get_object_or_404(Account, pk=self.kwargs["pk"])
        return account.transactionentry_set.all()
