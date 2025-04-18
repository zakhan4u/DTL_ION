from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='communication/login.html'), name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_note, name='create_note'),
    path('note/<str:note_id>/', views.view_note, name='view_note'),
    path('status/<str:note_id>/', views.update_status, name='update_status'),
    path('forward/<str:note_id>/', views.forward_note, name='forward_note'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='communication/password_change.html',
        success_url='/password/change/done/'
    ), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='communication/password_change_done.html'
    ), name='password_change_done'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]