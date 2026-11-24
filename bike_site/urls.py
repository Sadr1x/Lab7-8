from django.contrib.auth.views import LoginView
from django.urls import path

from repairdesk import views

urlpatterns = [
    path("", views.repair_list, name="repair-list"),
    path("repairs/<int:pk>/", views.repair_detail, name="repair-detail"),
    path("workbench/", views.workbench, name="staff-repairs"),
    path("accounts/login/", LoginView.as_view(), name="login"),
]
