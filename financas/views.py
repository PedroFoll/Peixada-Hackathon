import json
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from . import services
from .forms import CategoriaForm, MovimentacaoForm
from .models import Categoria, Movimentacao


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Gerar ocorrências pendentes de movimentações recorrentes
        services.processar_recorrencias_usuario(request.user)

        filtro = request.GET.get('periodo', 'mensal')

        if filtro == 'personalizado':
            data_inicio_str = request.GET.get('data_inicio', '')
            data_fim_str = request.GET.get('data_fim', '')
            try:
                data_inicio = date.fromisoformat(data_inicio_str)
                data_fim = date.fromisoformat(data_fim_str)
                if data_inicio > data_fim:
                    raise ValueError('data_inicio posterior a data_fim')
            except (ValueError, TypeError):
                data_inicio, data_fim = services.get_periodo('mensal')
                filtro = 'mensal'
        else:
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
                if mov.recorrente and mov.frequencia:
                    total = services.gerar_movimentacoes_recorrentes(mov)
                    messages.success(
                        request,
                        f'{mov.get_tipo_display()} adicionada com sucesso '
                        f'({total} ocorrência(s) recorrente(s) gerada(s)).',
                    )
                else:
                    messages.success(request, f'{mov.get_tipo_display()} adicionada com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao salvar movimentação: {e}')
        else:
            for erros in form.errors.values():
                for erro in erros:
                    messages.error(request, erro)
    else:
        messages.error(request, 'Método inválido.')
    _next = request.POST.get('_next', 'dashboard')
    return redirect('financas:lancamentos' if _next == 'lancamentos' else 'financas:dashboard')


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
    _next = request.POST.get('_next', 'dashboard')
    if _next == 'lancamentos':
        return redirect('financas:lancamentos')
    if _next == 'categorias':
        return redirect('financas:categorias')
    return redirect('financas:dashboard')


class LancamentosView(LoginRequiredMixin, View):
    def get(self, request):
        # Gerar ocorrências pendentes de movimentações recorrentes
        services.processar_recorrencias_usuario(request.user)

        data_inicio_str = request.GET.get('data_inicio', '')
        data_fim_str = request.GET.get('data_fim', '')
        tipo = request.GET.get('tipo', '')
        categoria_id = request.GET.get('categoria', '')
        descricao = request.GET.get('descricao', '')

        data_inicio = None
        data_fim = None
        try:
            if data_inicio_str:
                data_inicio = date.fromisoformat(data_inicio_str)
        except ValueError:
            data_inicio_str = ''
        try:
            if data_fim_str:
                data_fim = date.fromisoformat(data_fim_str)
        except ValueError:
            data_fim_str = ''

        qs = services.get_movimentacoes_filtradas(
            usuario=request.user,
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo=tipo or None,
            categoria_id=categoria_id or None,
            descricao=descricao or None,
        )

        totais = qs.aggregate(
            total_receitas=Sum('valor', filter=Q(tipo='receita'), default=Decimal('0')),
            total_despesas=Sum('valor', filter=Q(tipo='despesa'), default=Decimal('0')),
            total_count=Count('id'),
        )

        categorias = Categoria.objects.filter(usuario=request.user)

        paginator = Paginator(qs, 20)
        page = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)

        query_params = request.GET.copy()
        query_params.pop('page', None)

        context = {
            'page_obj': page_obj,
            'categorias': categorias,
            'filtros': {
                'data_inicio': data_inicio_str,
                'data_fim': data_fim_str,
                'tipo': tipo,
                'categoria': categoria_id,
                'descricao': descricao,
            },
            'query_string': query_params.urlencode(),
            'totais': totais,
        }
        return render(request, 'financas/lancamentos.html', context)


@login_required
def editar_movimentacao(request, pk):
    mov = get_object_or_404(Movimentacao, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, instance=mov, usuario=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Movimentação atualizada com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar movimentação: {e}')
        else:
            for erros in form.errors.values():
                for erro in erros:
                    messages.error(request, erro)
    else:
        messages.error(request, 'Método inválido.')
    return redirect('financas:lancamentos')


@login_required
def excluir_movimentacao(request, pk):
    mov = get_object_or_404(Movimentacao, pk=pk, usuario=request.user)
    if request.method == 'POST':
        try:
            desc = mov.descricao or 'sem descrição'
            mov.delete()
            messages.success(request, f'Movimentação "{desc}" excluída com sucesso.')
        except Exception as e:
            messages.error(request, f'Erro ao excluir movimentação: {e}')
    else:
        messages.error(request, 'Método inválido.')
    return redirect('financas:lancamentos')


@login_required
def categorias_placeholder(request):
    return render(request, 'financas/placeholder.html', {'titulo': 'Categorias'})


class CategoriasView(LoginRequiredMixin, View):
    def get(self, request):
        categorias = (
            Categoria.objects
            .filter(usuario=request.user)
            .annotate(total_movimentacoes=Count('movimentacoes'))
            .order_by('nome')
        )
        context = {
            'categorias': categorias,
            'total': categorias.count(),
        }
        return render(request, 'financas/categorias.html', context)


@login_required
def editar_categoria(request, pk):
    cat = get_object_or_404(Categoria, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=cat)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Categoria "{cat.nome}" atualizada com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar categoria: {e}')
        else:
            for erros in form.errors.values():
                for erro in erros:
                    messages.error(request, erro)
    else:
        messages.error(request, 'Método inválido.')
    return redirect('financas:categorias')


@login_required
def excluir_categoria(request, pk):
    cat = get_object_or_404(Categoria, pk=pk, usuario=request.user)
    if request.method == 'POST':
        if cat.movimentacoes.exists():
            messages.error(
                request,
                f'A categoria "{cat.nome}" possui movimentações vinculadas e não pode ser excluída. '
                'Edite ou remova as movimentações antes de excluir a categoria.',
            )
        else:
            try:
                nome = cat.nome
                cat.delete()
                messages.success(request, f'Categoria "{nome}" excluída com sucesso.')
            except Exception as e:
                messages.error(request, f'Erro ao excluir categoria: {e}')
    else:
        messages.error(request, 'Método inválido.')
    return redirect('financas:categorias')


