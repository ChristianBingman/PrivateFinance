from django.urls import path

from . import views

app_name = "acctmgr"
urlpatterns = [
    path("", views.index, name="account-index"),
    path("account/<int:pk>", views.index, name="account-view"),
    path(
        "account/<int:account_pk>/edit/<int:transactiondetail_pk>",
        views.edit,
        name="edit-xact-view",
    ),
]
