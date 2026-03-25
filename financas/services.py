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


def gerar_movimentacoes_recorrentes(movimentacao):
    """
    A partir de uma movimentação marcada como recorrente, gera as
    ocorrências pendentes até a data atual (nunca no futuro).

    Verifica quais datas já foram geradas (via movimentacao_origem)
    e cria apenas as faltantes.

    Retorna a quantidade de movimentações criadas.
    """
    if not movimentacao.recorrente or not movimentacao.frequencia:
        return 0

    hoje = date.today()
    data_inicio = movimentacao.data
    data_limite = movimentacao.data_limite or (data_inicio + timedelta(days=365))
    # Nunca gerar ocorrências com data após hoje
    data_limite = min(data_limite, hoje)

    datas = _calcular_datas_recorrentes(
        frequencia=movimentacao.frequencia,
        data_inicio=data_inicio,
        data_limite=data_limite,
        dias_semana=movimentacao.dias_semana,
        dia_mes=movimentacao.dia_mes,
    )

    if not datas:
        return 0

    # Buscar datas já geradas para esta movimentação recorrente
    datas_existentes = set(
        movimentacao.ocorrencias.values_list('data', flat=True)
    )

    novas = []
    for dt in datas:
        if dt not in datas_existentes:
            novas.append(Movimentacao(
                usuario=movimentacao.usuario,
                categoria=movimentacao.categoria,
                descricao=movimentacao.descricao,
                valor=movimentacao.valor,
                tipo=movimentacao.tipo,
                data=dt,
                recorrente=False,
                movimentacao_origem=movimentacao,
            ))

    if novas:
        Movimentacao.objects.bulk_create(novas)

    return len(novas)


def processar_recorrencias_usuario(usuario):
    """
    Processa todas as movimentações recorrentes de um usuário,
    gerando ocorrências pendentes até a data atual.
    """
    recorrentes = (
        Movimentacao.objects
        .filter(usuario=usuario, recorrente=True)
        .select_related('categoria')
    )
    total = 0
    for mov in recorrentes:
        total += gerar_movimentacoes_recorrentes(mov)
    return total


def _calcular_datas_recorrentes(frequencia, data_inicio, data_limite,
                                dias_semana=None, dia_mes=None):
    """Retorna lista de datas futuras (excluindo data_inicio) conforme a frequência."""
    datas = []

    if frequencia == 'diaria':
        dt = data_inicio + timedelta(days=1)
        while dt <= data_limite:
            datas.append(dt)
            dt += timedelta(days=1)

    elif frequencia == 'semanal':
        if not dias_semana:
            # Sem dias específicos: repete no mesmo dia da semana
            dt = data_inicio + timedelta(weeks=1)
            while dt <= data_limite:
                datas.append(dt)
                dt += timedelta(weeks=1)
        else:
            dias = [int(d) for d in dias_semana.split(',') if d.strip().isdigit()]
            dt = data_inicio + timedelta(days=1)
            while dt <= data_limite:
                if dt.weekday() in dias:
                    datas.append(dt)
                dt += timedelta(days=1)

    elif frequencia == 'mensal':
        dia = dia_mes or data_inicio.day
        mes = data_inicio.month
        ano = data_inicio.year

        # Avança para o próximo mês
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

        while True:
            dia_real = min(dia, _ultimo_dia_mes(ano, mes))
            dt = date(ano, mes, dia_real)
            if dt > data_limite:
                break
            datas.append(dt)
            mes += 1
            if mes > 12:
                mes = 1
                ano += 1

    return datas


def _ultimo_dia_mes(ano, mes):
    """Retorna o último dia do mês para o ano/mês informados."""
    if mes == 12:
        return 31
    return (date(ano, mes + 1, 1) - timedelta(days=1)).day


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


def get_movimentacoes_filtradas(usuario, data_inicio=None, data_fim=None,
                                tipo=None, categoria_id=None, descricao=None):
    """Retorna movimentações do usuário com filtros opcionais aplicados."""
    qs = (
        Movimentacao.objects
        .filter(usuario=usuario)
        .select_related('categoria')
    )
    if data_inicio:
        qs = qs.filter(data__gte=data_inicio)
    if data_fim:
        qs = qs.filter(data__lte=data_fim)
    if tipo in ('receita', 'despesa'):
        qs = qs.filter(tipo=tipo)
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if descricao:
        qs = qs.filter(descricao__icontains=descricao)
    return qs.order_by('-data', '-criado_em')
