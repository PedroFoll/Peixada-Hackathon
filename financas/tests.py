import json
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction

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


class CategoriaCrudTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.outro = criar_usuario('outro_cat', 'Senha@987')
        self.client.login(username='usuario_teste', password='Senha@123')
        self.url_criar = reverse('financas:criar_categoria')

    def test_cadastro_categoria_cria_no_banco(self):
        response = self.client.post(self.url_criar, {
            'nome': 'Moradia',
            'cor': '#112233',
            'icone': 'bi-house',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Categoria.objects.filter(usuario=self.usuario, nome='Moradia').exists())

    def test_nome_categoria_unico_por_usuario(self):
        criar_categoria(self.usuario, 'Lazer')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Categoria.objects.create(
                    usuario=self.usuario,
                    nome='Lazer',
                    cor='#111111',
                    icone='bi-star',
                )
        self.assertEqual(Categoria.objects.filter(usuario=self.usuario, nome='Lazer').count(), 1)

    def test_editar_categoria_existente(self):
        cat = criar_categoria(self.usuario, 'Mercado')
        url = reverse('financas:editar_categoria', kwargs={'pk': cat.pk})
        self.client.post(url, {'nome': 'Supermercado', 'cor': cat.cor, 'icone': cat.icone})
        cat.refresh_from_db()
        self.assertEqual(cat.nome, 'Supermercado')

    def test_excluir_categoria_sem_movimentacao(self):
        cat = criar_categoria(self.usuario, 'Temporaria')
        url = reverse('financas:excluir_categoria', kwargs={'pk': cat.pk})
        self.client.post(url)
        self.assertFalse(Categoria.objects.filter(pk=cat.pk).exists())

    def test_excluir_categoria_com_movimentacao_bloqueia(self):
        cat = criar_categoria(self.usuario, 'Bloqueada')
        criar_movimentacao(self.usuario, cat, tipo='despesa', valor='10.00')
        url = reverse('financas:excluir_categoria', kwargs={'pk': cat.pk})
        response = self.client.post(url, follow=True)
        self.assertTrue(Categoria.objects.filter(pk=cat.pk).exists())
        mensagens = [str(m) for m in response.context['messages']]
        self.assertTrue(any('não pode ser excluída' in m for m in mensagens))

    def test_outro_usuario_nao_edita_categoria(self):
        cat = criar_categoria(self.outro, 'Privada')
        url = reverse('financas:editar_categoria', kwargs={'pk': cat.pk})
        response = self.client.post(url, {'nome': 'Hack', 'cor': '#000000', 'icone': 'bi-x'})
        self.assertEqual(response.status_code, 404)


class MovimentacaoCrudERecorrenciaTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.cat = criar_categoria(self.usuario, 'Geral')
        self.client.login(username='usuario_teste', password='Senha@123')
        self.url_criar = reverse('financas:criar_movimentacao')

    def test_cadastro_despesa_pontual_com_obrigatorios(self):
        self.client.post(self.url_criar, {
            'tipo': 'despesa',
            'categoria': self.cat.pk,
            'valor': '75.50',
            'data': '2026-03-01',
            'descricao': 'Conta de luz',
        })
        self.assertTrue(Movimentacao.objects.filter(usuario=self.usuario, tipo='despesa', valor='75.50').exists())

    def test_cadastro_receita_pontual_com_obrigatorios(self):
        self.client.post(self.url_criar, {
            'tipo': 'receita',
            'categoria': self.cat.pk,
            'valor': '1200.00',
            'data': '2026-03-02',
            'descricao': 'Salario',
        })
        self.assertTrue(Movimentacao.objects.filter(usuario=self.usuario, tipo='receita', valor='1200.00').exists())

    def test_descricao_opcional_em_despesa(self):
        self.client.post(self.url_criar, {
            'tipo': 'despesa',
            'categoria': self.cat.pk,
            'valor': '10.00',
            'data': '2026-03-03',
            'descricao': '',
        })
        mov = Movimentacao.objects.get(usuario=self.usuario, tipo='despesa', valor='10.00')
        self.assertEqual(mov.descricao, '')

    def test_descricao_opcional_em_receita(self):
        self.client.post(self.url_criar, {
            'tipo': 'receita',
            'categoria': self.cat.pk,
            'valor': '20.00',
            'data': '2026-03-04',
            'descricao': '',
        })
        mov = Movimentacao.objects.get(usuario=self.usuario, tipo='receita', valor='20.00')
        self.assertEqual(mov.descricao, '')

    def test_recorrencia_diaria_gera_ocorrencias_ate_hoje(self):
        inicio = date.today() - timedelta(days=3)
        self.client.post(self.url_criar, {
            'tipo': 'despesa',
            'categoria': self.cat.pk,
            'valor': '5.00',
            'data': inicio.isoformat(),
            'descricao': 'Cafe',
            'recorrente': 'on',
            'frequencia': 'diaria',
        })
        pai = Movimentacao.objects.get(usuario=self.usuario, recorrente=True, descricao='Cafe')
        self.assertGreaterEqual(pai.ocorrencias.count(), 1)
        self.assertTrue(all(o.data <= date.today() for o in pai.ocorrencias.all()))

    def test_recorrencia_semanal_gera_ocorrencias(self):
        inicio = date.today() - timedelta(days=14)
        self.client.post(self.url_criar, {
            'tipo': 'receita',
            'categoria': self.cat.pk,
            'valor': '100.00',
            'data': inicio.isoformat(),
            'descricao': 'Freela',
            'recorrente': 'on',
            'frequencia': 'semanal',
            'dias_semana': [str(date.today().weekday())],
        })
        pai = Movimentacao.objects.get(usuario=self.usuario, recorrente=True, descricao='Freela')
        self.assertGreaterEqual(pai.ocorrencias.count(), 1)

    def test_recorrencia_mensal_gera_ocorrencias(self):
        inicio = date.today().replace(day=1) - timedelta(days=40)
        self.client.post(self.url_criar, {
            'tipo': 'despesa',
            'categoria': self.cat.pk,
            'valor': '55.00',
            'data': inicio.isoformat(),
            'descricao': 'Internet',
            'recorrente': 'on',
            'frequencia': 'mensal',
            'dia_mes': '5',
        })
        pai = Movimentacao.objects.get(usuario=self.usuario, recorrente=True, descricao='Internet')
        self.assertGreaterEqual(pai.ocorrencias.count(), 1)

    def test_recorrencia_respeita_data_limite(self):
        inicio = date.today() - timedelta(days=10)
        limite = date.today() - timedelta(days=5)
        self.client.post(self.url_criar, {
            'tipo': 'despesa',
            'categoria': self.cat.pk,
            'valor': '8.00',
            'data': inicio.isoformat(),
            'descricao': 'Teste limite',
            'recorrente': 'on',
            'frequencia': 'diaria',
            'data_limite': limite.isoformat(),
        })
        pai = Movimentacao.objects.get(usuario=self.usuario, recorrente=True, descricao='Teste limite')
        self.assertTrue(all(o.data <= limite for o in pai.ocorrencias.all()))

    def test_processamento_recorrencia_nao_duplica_ocorrencias(self):
        pai = Movimentacao.objects.create(
            usuario=self.usuario,
            categoria=self.cat,
            tipo='despesa',
            valor=Decimal('11.00'),
            data=date.today() - timedelta(days=5),
            descricao='Sem duplicar',
            recorrente=True,
            frequencia='diaria',
        )
        services.processar_recorrencias_usuario(self.usuario)
        qtd_1 = pai.ocorrencias.count()
        services.processar_recorrencias_usuario(self.usuario)
        pai.refresh_from_db()
        self.assertEqual(qtd_1, pai.ocorrencias.count())

    def test_editar_movimentacao(self):
        mov = criar_movimentacao(self.usuario, self.cat, tipo='despesa', valor='19.90', descricao='Antiga')
        url = reverse('financas:editar_movimentacao', kwargs={'pk': mov.pk})
        self.client.post(url, {
            'tipo': 'despesa',
            'categoria': self.cat.pk,
            'valor': '29.90',
            'data': mov.data.isoformat(),
            'descricao': 'Nova',
        })
        mov.refresh_from_db()
        self.assertEqual(mov.descricao, 'Nova')
        self.assertEqual(mov.valor, Decimal('29.90'))

    def test_excluir_movimentacao_apenas_post(self):
        mov = criar_movimentacao(self.usuario, self.cat, tipo='despesa', valor='22.00')
        url = reverse('financas:excluir_movimentacao', kwargs={'pk': mov.pk})
        self.client.get(url)
        self.assertTrue(Movimentacao.objects.filter(pk=mov.pk).exists())
        self.client.post(url)
        self.assertFalse(Movimentacao.objects.filter(pk=mov.pk).exists())


class LancamentosTabelaEFiltrosTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.cat_a = criar_categoria(self.usuario, 'Alimentacao')
        self.cat_t = criar_categoria(self.usuario, 'Transporte')
        self.client.login(username='usuario_teste', password='Senha@123')
        self.url = reverse('financas:lancamentos')

        criar_movimentacao(self.usuario, self.cat_a, tipo='despesa', valor='100.00',
                           data=date(2026, 1, 10), descricao='Mercado semanal')
        criar_movimentacao(self.usuario, self.cat_t, tipo='despesa', valor='50.00',
                           data=date(2026, 1, 20), descricao='Uber centro')
        criar_movimentacao(self.usuario, self.cat_a, tipo='receita', valor='900.00',
                           data=date(2026, 2, 5), descricao='Bonus')

    def test_tabela_exibe_dados_corretos(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Mercado semanal')
        self.assertContains(response, 'Uber centro')
        self.assertContains(response, 'Bonus')

    def test_filtro_por_data(self):
        response = self.client.get(self.url, {
            'data_inicio': '2026-02-01',
            'data_fim': '2026-02-28',
        })
        self.assertContains(response, 'Bonus')
        self.assertNotContains(response, 'Mercado semanal')

    def test_filtro_por_categoria(self):
        response = self.client.get(self.url, {'categoria': str(self.cat_t.pk)})
        self.assertContains(response, 'Uber centro')
        self.assertNotContains(response, 'Mercado semanal')

    def test_filtro_por_tipo(self):
        response = self.client.get(self.url, {'tipo': 'receita'})
        self.assertContains(response, 'Bonus')
        self.assertNotContains(response, 'Uber centro')

    def test_filtro_por_descricao(self):
        response = self.client.get(self.url, {'descricao': 'uber'})
        self.assertContains(response, 'Uber centro')
        self.assertNotContains(response, 'Mercado semanal')

    def test_diferenciacao_visual_receita_despesa(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'text-success')
        self.assertContains(response, 'text-danger')


class GraficosEDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.cat_rec = criar_categoria(self.usuario, 'Salario')
        self.cat_des = criar_categoria(self.usuario, 'Contas')
        self.client.login(username='usuario_teste', password='Senha@123')
        self.url = reverse('financas:dashboard')

        criar_movimentacao(self.usuario, self.cat_rec, tipo='receita', valor='2000.00', data=date(2026, 1, 5))
        criar_movimentacao(self.usuario, self.cat_des, tipo='despesa', valor='500.00', data=date(2026, 1, 10))
        criar_movimentacao(self.usuario, self.cat_des, tipo='despesa', valor='300.00', data=date(2026, 2, 10))

    def test_contexto_json_dos_graficos(self):
        response = self.client.get(self.url, {'periodo': 'anual'})
        comparacao = json.loads(response.context['comparacao_json'])
        receitas_cat = json.loads(response.context['receitas_cat_json'])
        despesas_cat = json.loads(response.context['despesas_cat_json'])
        self.assertIn('labels', comparacao)
        self.assertIn('receitas', comparacao)
        self.assertIn('despesas', comparacao)
        self.assertIn('labels', receitas_cat)
        self.assertIn('valores', despesas_cat)

    def test_comparacao_receita_despesa_calcula_corretamente(self):
        response = self.client.get(self.url, {'periodo': 'anual'})
        totais = response.context['totais']
        self.assertEqual(totais['total_receitas'], Decimal('2000.00'))
        self.assertEqual(totais['total_despesas'], Decimal('800.00'))
        self.assertEqual(totais['saldo'], Decimal('1200.00'))

    def test_graficos_respeitam_intervalo_personalizado(self):
        response = self.client.get(self.url, {
            'periodo': 'personalizado',
            'data_inicio': '2026-02-01',
            'data_fim': '2026-02-28',
        })
        totais = response.context['totais']
        self.assertEqual(totais['total_receitas'], Decimal('0'))
        self.assertEqual(totais['total_despesas'], Decimal('300.00'))


class ModaisEResponsividadeTemplateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.cat = criar_categoria(self.usuario)
        self.client.login(username='usuario_teste', password='Senha@123')

    def test_modal_novo_movimentacao_dashboard_presente(self):
        response = self.client.get(reverse('financas:dashboard'))
        self.assertContains(response, 'id="modalNovoLancamento"')
        self.assertContains(response, 'id="n-recorrente"')
        self.assertContains(response, 'id="n-frequencia"')
        self.assertContains(response, 'id="n-data-limite"')

    def test_modal_edicao_lancamentos_presente(self):
        response = self.client.get(reverse('financas:lancamentos'))
        self.assertContains(response, 'id="modalEditarLancamento"')
        self.assertContains(response, 'id="e-recorrente"')
        self.assertContains(response, 'id="e-frequencia"')

    def test_classes_responsivas_presentes_em_telas_principais(self):
        dash = self.client.get(reverse('financas:dashboard'))
        lanc = self.client.get(reverse('financas:lancamentos'))
        self.assertContains(dash, 'col-12 col-sm-6 col-xl-3')
        self.assertContains(lanc, 'col-12 col-md-6 col-lg-3')


class SegurancaEAutorizacaoFinancasTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.outro = criar_usuario('outro_seg', 'Senha@456')
        self.cat_usuario = criar_categoria(self.usuario)
        self.mov_outro = criar_movimentacao(
            self.outro,
            criar_categoria(self.outro, 'Privada'),
            tipo='despesa',
            valor='77.00',
        )

    def test_paginas_restritas_exigem_login(self):
        for name in ['financas:dashboard', 'financas:lancamentos', 'financas:categorias']:
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('usuarios:login'), response.url)

    def test_usuario_nao_pode_editar_movimentacao_de_outro(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        url = reverse('financas:editar_movimentacao', kwargs={'pk': self.mov_outro.pk})
        response = self.client.post(url, {
            'tipo': 'despesa',
            'categoria': self.cat_usuario.pk,
            'valor': '99.00',
            'data': date.today().isoformat(),
            'descricao': 'Tentativa',
        })
        self.assertEqual(response.status_code, 404)

    def test_usuario_nao_pode_excluir_movimentacao_de_outro(self):
        self.client.login(username='usuario_teste', password='Senha@123')
        url = reverse('financas:excluir_movimentacao', kwargs={'pk': self.mov_outro.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Movimentacao.objects.filter(pk=self.mov_outro.pk).exists())


class PerformanceSmokeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.cat = criar_categoria(self.usuario, 'Performance')
        self.client.login(username='usuario_teste', password='Senha@123')

    def test_lancamentos_com_grande_volume_responde_rapido_e_paginado(self):
        base = date(2026, 1, 1)
        lote = []
        for i in range(2000):
            lote.append(Movimentacao(
                usuario=self.usuario,
                categoria=self.cat,
                tipo='despesa' if i % 2 else 'receita',
                valor=Decimal('1.00'),
                data=base + timedelta(days=(i % 28)),
                descricao=f'Item {i}',
            ))
        Movimentacao.objects.bulk_create(lote)

        response = self.client.get(reverse('financas:lancamentos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['totais']['total_count'], 2000)
        self.assertEqual(len(response.context['page_obj'].object_list), 20)


class Pagina404CustomizadaTest(TestCase):
    @override_settings(DEBUG=True)
    def test_rota_inexistente_exibe_404_customizada_em_debug(self):
        response = self.client.get('/rota-que-nao-existe/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
        self.assertContains(response, 'Ops! Pagina nao encontrada (404)', status_code=404)

    @override_settings(DEBUG=False)
    def test_rota_inexistente_exibe_404_customizada_em_producao(self):
        response = self.client.get('/outra-rota-inexistente/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')


class MenuLateralResponsivoTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.usuario = criar_usuario()
        self.cat = criar_categoria(self.usuario)
        self.client.login(username='usuario_teste', password='Senha@123')

    def _assert_menu_mobile(self, response):
        self.assertContains(response, 'class="topbar d-md-none d-flex')
        self.assertContains(response, 'data-bs-target="#sidebarMobile"')
        self.assertContains(response, 'id="sidebarMobile"')

    def test_menu_mobile_renderiza_no_dashboard(self):
        response = self.client.get(reverse('financas:dashboard'))
        self._assert_menu_mobile(response)

    def test_menu_mobile_renderiza_em_lancamentos(self):
        response = self.client.get(reverse('financas:lancamentos'))
        self._assert_menu_mobile(response)

    def test_menu_mobile_renderiza_em_categorias(self):
        response = self.client.get(reverse('financas:categorias'))
        self._assert_menu_mobile(response)

