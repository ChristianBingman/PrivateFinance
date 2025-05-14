from django.urls import path

from . import views

app_name = "acctmgr"
urlpatterns = [path("", views.AccountView.as_view(), name="index")]
