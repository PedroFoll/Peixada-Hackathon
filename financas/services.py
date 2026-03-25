import json
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth

from .models import Movimentacao


def get_periodo(filtro):
    hoje = date.today()
    if filtro == 'semanal':
        inicio = hoje - timedelta(days=hoje.weekday())
        return inicio, hoje
    elif filtro == 'anual':
        return date(hoje.year, 1, 1), hoje
    else:  # mensal (padrão)
        return date(hoje.year, hoje.month, 1), hoje


def calcular_totais(usuario, data_inicio, data_fim):
    qs = Movimentacao.objects.filter(
        usuario=usuario,
        data__gte=data_inicio,
        data__lte=data_fim,
    )
    resultado = qs.aggregate(
        total_receitas=Sum('valor', filter=Q(tipo='receita'), default=Decimal('0')),
        total_despesas=Sum('valor', filter=Q(tipo='despesa'), default=Decimal('0')),
    )
    resultado['saldo'] = resultado['total_receitas'] - resultado['total_despesas']
    return resultado


def get_dados_comparacao_mensal(usuario, data_inicio, data_fim):
    qs = Movimentacao.objects.filter(
        usuario=usuario,
        data__gte=data_inicio,
        data__lte=data_fim,
    )

    receitas = (
        qs.filter(tipo='receita')
        .annotate(mes=TruncMonth('data'))
        .values('mes')
        .annotate(total=Sum('valor'))
        .order_by('mes')
    )
    despesas = (
        qs.filter(tipo='despesa')
        .annotate(mes=TruncMonth('data'))
        .values('mes')
        .annotate(total=Sum('valor'))
        .order_by('mes')
    )

    labels_set = set()
    for r in receitas:
        labels_set.add(r['mes'])
    for d in despesas:
        labels_set.add(d['mes'])

    labels = sorted(labels_set)
    receitas_dict = {r['mes']: float(r['total']) for r in receitas}
    despesas_dict = {d['mes']: float(d['total']) for d in despesas}

    return {
        'labels': [l.strftime('%b/%Y') for l in labels],
        'receitas': [receitas_dict.get(l, 0) for l in labels],
        'despesas': [despesas_dict.get(l, 0) for l in labels],
    }


def get_dados_por_categoria(usuario, tipo, data_inicio, data_fim):
    qs = (
        Movimentacao.objects
        .filter(usuario=usuario, tipo=tipo, data__gte=data_inicio, data__lte=data_fim)
        .select_related('categoria')
        .values('categoria__nome', 'categoria__cor')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )

    labels, valores, cores = [], [], []
    for item in qs:
        labels.append(item['categoria__nome'] or 'Sem categoria')
        valores.append(float(item['total']))
        cores.append(item['categoria__cor'] or '#6c757d')

    return {'labels': labels, 'valores': valores, 'cores': cores}


def get_ultimas_movimentacoes(usuario, limite=8):
    return (
        Movimentacao.objects
        .filter(usuario=usuario)
        .select_related('categoria')
        .order_by('-data', '-criado_em')[:limite]
    )
