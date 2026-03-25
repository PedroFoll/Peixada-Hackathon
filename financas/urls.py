from django.urls import path
from . import views

app_name = 'financas'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]
