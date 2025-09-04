from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.register_view, name="signup"),
]
