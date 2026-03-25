import json
from datetime import date
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Categoria, Movimentacao
from . import services


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def criar_usuario(username='usuario_teste', password='Senha@123'):
    return User.objects.create_user(username=username, password=password)


def criar_categoria(usuario, nome='Alimentação', cor='#198754'):
    return Categoria.objects.create(usuario=usuario, nome=nome, cor=cor)


def criar_movimentacao(usuario, categoria, tipo='receita', valor='100.00',
                       data=None, descricao=''):
    return Movimentacao.objects.create(
        usuario=usuario,
        categoria=categoria,
        tipo=tipo,
        valor=Decimal(valor),
        data=data or date.today(),
        descricao=descricao,
    )


# ---------------------------------------------------------------------------
# Services — get_periodo
# ---------------------------------------------------------------------------

class GetPeriodoTest(TestCase):
    def test_periodo_mensal_inicia_no_primeiro_do_mes(self):
        inicio, fim = services.get_periodo('mensal')
        self.assertEqual(inicio.day, 1)
        self.assertEqual(inicio.month, date.today().month)
        self.assertEqual(fim, date.today())

    def test_periodo_semanal_inicia_na_segunda_feira(self):
        inicio, fim = services.get_periodo('semanal')
        self.assertEqual(inicio.weekday(), 0)  # segunda-feira
        self.assertEqual(fim, date.today())

    def test_periodo_anual_inicia_em_janeiro(self):
        inicio, fim = services.get_periodo('anual')
        self.assertEqual(inicio, date(date.today().year, 1, 1))
        self.assertEqual(fim, date.today())

    def test_periodo_desconhecido_retorna_mensal(self):
        inicio, fim = services.get_periodo('invalido')
        self.assertEqual(inicio.day, 1)
        self.assertEqual(inicio.month, date.today().month)


# ---------------------------------------------------------------------------
# Services — calcular_totais
# ---------------------------------------------------------------------------

class CalcularTotaisTest(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()
        self.outro_usuario = criar_usuario('outro', 'Senha@456')
        self.cat = criar_categoria(self.usuario)
        self.inicio = date(2026, 1, 1)
        self.fim = date(2026, 12, 31)

    def test_retorna_zeros_sem_movimentacoes(self):
        totais = services.calcular_totais(self.usuario, self.inicio, self.fim)
        self.assertEqual(totais['total_receitas'], Decimal('0'))
        self.assertEqual(totais['total_despesas'], Decimal('0'))
        self.assertEqual(totais['saldo'], Decimal('0'))

    def test_soma_receitas_corretamente(self):
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='300.00', data=date(2026, 3, 1))
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='200.00', data=date(2026, 4, 1))
        totais = services.calcular_totais(self.usuario, self.inicio, self.fim)
        self.assertEqual(totais['total_receitas'], Decimal('500.00'))

    def test_soma_despesas_corretamente(self):
        criar_movimentacao(self.usuario, self.cat, tipo='despesa', valor='150.00', data=date(2026, 2, 1))
        totais = services.calcular_totais(self.usuario, self.inicio, self.fim)
        self.assertEqual(totais['total_despesas'], Decimal('150.00'))

    def test_saldo_e_receitas_menos_despesas(self):
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='1000.00', data=date(2026, 1, 10))
        criar_movimentacao(self.usuario, self.cat, tipo='despesa', valor='400.00', data=date(2026, 1, 15))
        totais = services.calcular_totais(self.usuario, self.inicio, self.fim)
        self.assertEqual(totais['saldo'], Decimal('600.00'))

    def test_nao_inclui_movimentacoes_fora_do_periodo(self):
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='999.00', data=date(2025, 12, 31))
        totais = services.calcular_totais(self.usuario, self.inicio, self.fim)
        self.assertEqual(totais['total_receitas'], Decimal('0'))

    def test_isolamento_entre_usuarios(self):
        cat_outro = criar_categoria(self.outro_usuario, 'Salário')
        criar_movimentacao(self.outro_usuario, cat_outro, tipo='receita', valor='9999.00', data=date(2026, 1, 1))
        totais = services.calcular_totais(self.usuario, self.inicio, self.fim)
        self.assertEqual(totais['total_receitas'], Decimal('0'))


# ---------------------------------------------------------------------------
# Services — get_dados_comparacao_mensal
# ---------------------------------------------------------------------------

class GetDadosComparacaoMensalTest(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()
        self.cat = criar_categoria(self.usuario)
        self.inicio = date(2026, 1, 1)
        self.fim = date(2026, 12, 31)

    def test_retorna_estrutura_correta_sem_dados(self):
        dados = services.get_dados_comparacao_mensal(self.usuario, self.inicio, self.fim)
        self.assertIn('labels', dados)
        self.assertIn('receitas', dados)
        self.assertIn('despesas', dados)
        self.assertEqual(dados['labels'], [])

    def test_agrupa_por_mes(self):
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='100.00', data=date(2026, 1, 5))
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='200.00', data=date(2026, 1, 20))
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='500.00', data=date(2026, 2, 10))
        dados = services.get_dados_comparacao_mensal(self.usuario, self.inicio, self.fim)
        self.assertEqual(len(dados['labels']), 2)
        self.assertAlmostEqual(dados['receitas'][0], 300.0)
        self.assertAlmostEqual(dados['receitas'][1], 500.0)

    def test_despesas_zero_em_mes_sem_despesa(self):
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='100.00', data=date(2026, 3, 1))
        dados = services.get_dados_comparacao_mensal(self.usuario, self.inicio, self.fim)
        self.assertAlmostEqual(dados['despesas'][0], 0.0)


# ---------------------------------------------------------------------------
# Services — get_dados_por_categoria
# ---------------------------------------------------------------------------

class GetDadosPorCategoriaTest(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()
        self.outro_usuario = criar_usuario('outro2', 'Senha@999')
        self.cat1 = criar_categoria(self.usuario, 'Alimentação', '#198754')
        self.cat2 = criar_categoria(self.usuario, 'Transporte', '#0d6efd')
        self.inicio = date(2026, 1, 1)
        self.fim = date(2026, 12, 31)

    def test_retorna_listas_vazias_sem_dados(self):
        dados = services.get_dados_por_categoria(self.usuario, 'despesa', self.inicio, self.fim)
        self.assertEqual(dados['labels'], [])
        self.assertEqual(dados['valores'], [])
        self.assertEqual(dados['cores'], [])

    def test_agrupa_por_categoria(self):
        criar_movimentacao(self.usuario, self.cat1, tipo='despesa', valor='80.00', data=date(2026, 2, 1))
        criar_movimentacao(self.usuario, self.cat1, tipo='despesa', valor='20.00', data=date(2026, 2, 5))
        criar_movimentacao(self.usuario, self.cat2, tipo='despesa', valor='50.00', data=date(2026, 2, 10))
        dados = services.get_dados_por_categoria(self.usuario, 'despesa', self.inicio, self.fim)
        self.assertEqual(len(dados['labels']), 2)
        self.assertIn('Alimentação', dados['labels'])
        self.assertIn('Transporte', dados['labels'])

    def test_cores_retornadas_corretamente(self):
        criar_movimentacao(self.usuario, self.cat1, tipo='despesa', valor='50.00', data=date(2026, 1, 1))
        dados = services.get_dados_por_categoria(self.usuario, 'despesa', self.inicio, self.fim)
        self.assertIn('#198754', dados['cores'])

    def test_nao_retorna_tipo_errado(self):
        criar_movimentacao(self.usuario, self.cat1, tipo='receita', valor='500.00', data=date(2026, 1, 1))
        dados = services.get_dados_por_categoria(self.usuario, 'despesa', self.inicio, self.fim)
        self.assertEqual(dados['labels'], [])

    def test_isolamento_entre_usuarios(self):
        cat_outro = criar_categoria(self.outro_usuario, 'Outros')
        criar_movimentacao(self.outro_usuario, cat_outro, tipo='despesa', valor='999.00', data=date(2026, 1, 1))
        dados = services.get_dados_por_categoria(self.usuario, 'despesa', self.inicio, self.fim)
        self.assertEqual(dados['labels'], [])


# ---------------------------------------------------------------------------
# Services — get_ultimas_movimentacoes
# ---------------------------------------------------------------------------

class GetUltimasMovimentacoesTest(TestCase):
    def setUp(self):
        self.usuario = criar_usuario()
        self.outro_usuario = criar_usuario('outro3', 'Senha@777')
        self.cat = criar_categoria(self.usuario)

    def test_retorna_apenas_movimentacoes_do_usuario(self):
        cat_outro = criar_categoria(self.outro_usuario, 'Outros')
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='100.00')
        criar_movimentacao(self.outro_usuario, cat_outro, tipo='receita', valor='999.00')
        resultado = list(services.get_ultimas_movimentacoes(self.usuario))
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].usuario, self.usuario)

    def test_limite_padrao_e_8(self):
        for i in range(12):
            criar_movimentacao(self.usuario, self.cat, tipo='despesa', valor='10.00',
                               data=date(2026, 1, i + 1))
        resultado = list(services.get_ultimas_movimentacoes(self.usuario))
        self.assertEqual(len(resultado), 8)

    def test_limite_customizado(self):
        for i in range(5):
            criar_movimentacao(self.usuario, self.cat, tipo='despesa', valor='10.00',
                               data=date(2026, 1, i + 1))
        resultado = list(services.get_ultimas_movimentacoes(self.usuario, limite=3))
        self.assertEqual(len(resultado), 3)

    def test_ordem_decrescente_por_data(self):
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='100.00', data=date(2026, 1, 1))
        criar_movimentacao(self.usuario, self.cat, tipo='receita', valor='200.00', data=date(2026, 3, 1))
        resultado = list(services.get_ultimas_movimentacoes(self.usuario))
        self.assertGreaterEqual(resultado[0].data, resultado[1].data)

    def test_retorna_lista_vazia_sem_movimentacoes(self):
        resultado = list(services.get_ultimas_movimentacoes(self.usuario))
        self.assertEqual(resultado, [])


# ---------------------------------------------------------------------------
# View — DashboardView
# ---------------------------------------------------------------------------

class DashboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('financas:dashboard')
        self.usuario = criar_usuario()
        self.cat = criar_categoria(self.usuario)

    def test_usuario_nao_autenticado_redireciona_para_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{reverse('usuarios:login')}?next={self.url}",
                             fetch_redirect_response=False)

    def test_usuario_autenticado_acessa_dashboard(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'financas/dashboard.html')

    def test_contexto_contem_chaves_obrigatorias(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        response = self.client.get(self.url)
        for chave in ('filtro', 'data_inicio', 'data_fim', 'totais',
                      'comparacao_json', 'receitas_cat_json',
                      'despesas_cat_json', 'ultimas_movimentacoes'):
            self.assertIn(chave, response.context, msg=f"Chave '{chave}' ausente no contexto")

    def test_filtro_padrao_e_mensal(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        response = self.client.get(self.url)
        self.assertEqual(response.context['filtro'], 'mensal')

    def test_filtro_semanal_via_get(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        response = self.client.get(self.url, {'periodo': 'semanal'})
        self.assertEqual(response.context['filtro'], 'semanal')

    def test_filtro_anual_via_get(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        response = self.client.get(self.url, {'periodo': 'anual'})
        self.assertEqual(response.context['filtro'], 'anual')

    def test_comparacao_json_e_json_valido(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        response = self.client.get(self.url)
        dados = json.loads(response.context['comparacao_json'])
        self.assertIn('labels', dados)
        self.assertIn('receitas', dados)
        self.assertIn('despesas', dados)

    def test_nao_exibe_dados_de_outro_usuario(self):
        outro = criar_usuario('invasor', 'Senha@000')
        cat_outro = criar_categoria(outro, 'Outros')
        criar_movimentacao(outro, cat_outro, tipo='receita', valor='99999.00')

        self.client.login(username='usuario_teste', password='Senha@123')
        response = self.client.get(self.url)
        totais = response.context['totais']
        self.assertEqual(totais['total_receitas'], Decimal('0'))

