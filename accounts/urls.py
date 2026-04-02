from django.urls import path
from . import views

urlpatterns = [
    # Dashboard session
    path('admin-login/', views.admin_login_view, name='admin-login'),

    # Auth API
    path('admin-token/', views.admin_token_login, name='admin-token'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Profil
    path('profile/', views.get_profile, name='get-profile'),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('profile/change-password/', views.change_password, name='change-password'),

    # CRUD users (admin)
    path('users/', views.get_all_users, name='get-all-users'),
    path('users/delete-all/', views.delete_all_users, name='delete-all-users'),
    path('users/<uuid:user_id>/', views.get_user_by_id, name='get-user-by-id'),
    path('users/<uuid:user_id>/update/', views.update_user, name='update-user'),
    path('users/<uuid:user_id>/delete/', views.delete_user, name='delete-user'),
]