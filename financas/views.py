import json

from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View

from . import services
from .forms import CategoriaForm, MovimentacaoForm
from .models import Categoria


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        filtro = request.GET.get('periodo', 'mensal')
        data_inicio, data_fim = services.get_periodo(filtro)

        totais = services.calcular_totais(request.user, data_inicio, data_fim)
        comparacao = services.get_dados_comparacao_mensal(request.user, data_inicio, data_fim)
        receitas_cat = services.get_dados_por_categoria(request.user, 'receita', data_inicio, data_fim)
        despesas_cat = services.get_dados_por_categoria(request.user, 'despesa', data_inicio, data_fim)
        ultimas = services.get_ultimas_movimentacoes(request.user)
        categorias = Categoria.objects.filter(usuario=request.user)

        context = {
            'filtro': filtro,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'totais': totais,
            'comparacao_json': json.dumps(comparacao),
            'receitas_cat_json': json.dumps(receitas_cat),
            'despesas_cat_json': json.dumps(despesas_cat),
            'ultimas_movimentacoes': ultimas,
            'categorias': categorias,
        }
        return render(request, 'financas/dashboard.html', context)


def home(request):
    return redirect('usuarios:login')


@login_required
def criar_movimentacao(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, usuario=request.user)
        if form.is_valid():
            try:
                mov = form.save(commit=False)
                mov.usuario = request.user
                mov.save()
                messages.success(request, f'{mov.get_tipo_display()} adicionada com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao salvar movimentação: {e}')
        else:
            for erros in form.errors.values():
                for erro in erros:
                    messages.error(request, erro)
    else:
        messages.error(request, 'Método inválido.')
    return redirect('financas:dashboard')


@login_required
def criar_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            try:
                cat = form.save(commit=False)
                cat.usuario = request.user
                cat.save()
                messages.success(request, f'Categoria "{cat.nome}" criada com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao criar categoria: {e}')
        else:
            for erros in form.errors.values():
                for erro in erros:
                    messages.error(request, erro)
    else:
        messages.error(request, 'Método inválido.')
    return redirect('financas:dashboard')


@login_required
def lancamentos_placeholder(request):
    return render(request, 'financas/placeholder.html', {'titulo': 'Lançamentos'})


@login_required
def categorias_placeholder(request):
    return render(request, 'financas/placeholder.html', {'titulo': 'Categorias'})


