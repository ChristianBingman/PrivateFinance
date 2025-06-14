from django.urls import path, re_path

from . import views

app_name = "currencymgr"
urlpatterns = [
    re_path(r"^(?P<pk>[0-9]+)?$", views.currency_editor, name="currency-editor"),
    path("<int:pk>/delete", views.currency_delete, name="currency-delete"),
]
