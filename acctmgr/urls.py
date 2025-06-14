from django.urls import path, re_path

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
    re_path(
        r"^account-editor/(?P<pk>[0-9]+)?$", views.account_editor, name="account-editor"
    ),
    path("account-editor/<int:pk>/delete", views.account_delete, name="account-delete"),
]
