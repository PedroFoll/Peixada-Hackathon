from django.urls import path
from . import views

app_name = 'financas'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('lancamentos/', views.LancamentosView.as_view(), name='lancamentos'),
    path('categorias/', views.categorias_placeholder, name='categorias'),
    path('movimentacoes/criar/', views.criar_movimentacao, name='criar_movimentacao'),
    path('movimentacoes/<int:pk>/editar/', views.editar_movimentacao, name='editar_movimentacao'),
    path('movimentacoes/<int:pk>/excluir/', views.excluir_movimentacao, name='excluir_movimentacao'),
    path('categorias/criar/', views.criar_categoria, name='criar_categoria'),
]
