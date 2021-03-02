from django.urls import path
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .views import AccountsView

urlpatterns = [
    path('login/', AccountsView.user_login),
    path('logout/', AccountsView.user_logout),
    path('register/',AccountsView. register),
    path('activate/', AccountsView.activate_account),
    path('reset_password/', PasswordResetView.as_view(template_name='password/reset.html'),
        name='reset_password'),
    path('reset_password_sent/', PasswordResetDoneView.as_view(template_name='password/sent.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='password/form.html'),
        name='password_reset_confirm'),
    path('reset_password_complete/', PasswordResetCompleteView.as_view(template_name='password/done.html'),
        name='password_reset_complete'),
]