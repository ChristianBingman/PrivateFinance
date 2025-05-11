from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("This will display the list of transactions for an account.")
