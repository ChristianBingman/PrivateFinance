from django.urls import path

from . import views

app_name = "acctmgr"
urlpatterns = [
    path("", views.index, name="account-index"),
    path("account/<int:pk>", views.index, name="account-view"),
    path(
        "account/<int:pk>/edit/<int:transaction_pk>",
        views.index,
        name="edit-xact-view",
    ),
]
