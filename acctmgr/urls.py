from django.urls import path

from . import views

app_name = "acctmgr"
urlpatterns = [path("", views.index, name="index")]
