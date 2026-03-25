import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .forms import CadastroForm, PerfilForm, AlterarSenhaForm


class LoginRedirectView(LoginView):
    template_name = 'usuarios/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('financas:dashboard')
        return super().dispatch(request, *args, **kwargs)

logger = logging.getLogger(__name__)


def cadastro(request):
    if request.user.is_authenticated:
        return redirect('financas:dashboard')
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bem-vindo(a), {user.first_name}! Sua conta foi criada.')
            return redirect('financas:dashboard')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = CadastroForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})


@login_required
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = PerfilForm(instance=request.user)
    return render(request, 'usuarios/perfil.html', {'form': form})


@login_required
def alterar_senha(request):
    if request.method == 'POST':
        form = AlterarSenhaForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso.')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Corrija os erros abaixo.')
    else:
        form = AlterarSenhaForm(request.user)
    return render(request, 'usuarios/alterar_senha.html', {'form': form})
