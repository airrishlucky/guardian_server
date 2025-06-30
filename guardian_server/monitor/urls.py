from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard),
    path("api/data/", views.receive_data, name="receive_data"),
    path("api/latest/", views.api_latest_data, name="api_latest_data"),
    path("history/", views.history_view, name="history"),
    path("location/", views.location_page, name="location_page"),
    path("notifications/", views.notification_history, name="notification_history"),
]
