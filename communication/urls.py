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
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_add, name='inventory_add'),
    path('inventory/edit/<int:item_id>/', views.inventory_edit, name='inventory_edit'),
    path('inventory/delete/<int:item_id>/', views.inventory_delete, name='inventory_delete'),
    path('stores/', views.stores_request, name='stores_request'),
    path('request/approve/<int:request_id>/', views.request_approve, name='request_approve'),
]