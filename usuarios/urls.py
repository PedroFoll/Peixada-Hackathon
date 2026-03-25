from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.LoginRedirectView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('perfil/', views.perfil, name='perfil'),
    path('alterar-senha/', views.alterar_senha, name='alterar_senha'),
]
