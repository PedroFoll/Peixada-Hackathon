from django.urls import path
from . import views

app_name = 'financas'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('lancamentos/', views.lancamentos_placeholder, name='lancamentos'),
    path('categorias/', views.categorias_placeholder, name='categorias'),
    path('movimentacoes/criar/', views.criar_movimentacao, name='criar_movimentacao'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
]
