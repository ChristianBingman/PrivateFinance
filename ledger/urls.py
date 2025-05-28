from django.urls import path

from . import views

app_name = "ledger"
urlpatterns = [
    path("create-transaction", views.xact_create, name="xact-create"),
]
