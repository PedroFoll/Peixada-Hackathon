import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from financas.models import Categoria, Movimentacao


CATEGORIAS_DESPESA = [
    {'nome': 'Alimentação', 'cor': '#e74c3c', 'icone': 'bi-cart'},
    {'nome': 'Transporte', 'cor': '#3498db', 'icone': 'bi-bus-front'},
    {'nome': 'Lazer', 'cor': '#9b59b6', 'icone': 'bi-controller'},
    {'nome': 'Saúde', 'cor': '#1abc9c', 'icone': 'bi-heart-pulse'},
    {'nome': 'Educação', 'cor': '#f39c12', 'icone': 'bi-book'},
    {'nome': 'Moradia', 'cor': '#e67e22', 'icone': 'bi-house'},
    {'nome': 'Outros', 'cor': '#95a5a6', 'icone': 'bi-three-dots'},
]

CATEGORIAS_RECEITA = [
    {'nome': 'Salário', 'cor': '#27ae60', 'icone': 'bi-wallet2'},
    {'nome': 'Freelance', 'cor': '#2ecc71', 'icone': 'bi-laptop'},
    {'nome': 'Investimentos', 'cor': '#16a085', 'icone': 'bi-graph-up-arrow'},
    {'nome': 'Presentes', 'cor': '#e91e63', 'icone': 'bi-gift'},
    {'nome': 'Outros', 'cor': '#7f8c8d', 'icone': 'bi-three-dots'},
]

MOVIMENTACOES_DESPESA = [
    {'categoria': 'Alimentação', 'descricao': 'Alimentação - Exemplo', 'min': 50, 'max': 500},
    {'categoria': 'Transporte', 'descricao': 'Transporte - Exemplo', 'min': 30, 'max': 150},
    {'categoria': 'Saúde', 'descricao': 'Saúde - Exemplo', 'min': 100, 'max': 1000},
    {'categoria': 'Moradia', 'descricao': 'Aluguel - Exemplo', 'fixo': 1200},
    {'categoria': 'Lazer', 'descricao': 'Lazer - Exemplo', 'min': 30, 'max': 300},
    {'categoria': 'Educação', 'descricao': 'Educação - Exemplo', 'min': 50, 'max': 500},
]

MOVIMENTACOES_RECEITA = [
    {'categoria': 'Salário', 'descricao': 'Salário - Exemplo', 'fixo': 3000},
    {'categoria': 'Freelance', 'descricao': 'Freelance - Exemplo', 'min': 500, 'max': 2000},
    {'categoria': 'Investimentos', 'descricao': 'Investimentos - Exemplo', 'min': 100, 'max': 1000},
    {'categoria': 'Presentes', 'descricao': 'Presentes - Exemplo', 'min': 50, 'max': 500},
]


def _gerar_valor(config):
    if 'fixo' in config:
        return Decimal(str(config['fixo']))
    return Decimal(str(random.randint(config['min'], config['max'])))


def _data_aleatoria_ultimo_trimestre():
    hoje = date.today()
    inicio = hoje - timedelta(days=90)
    delta = random.randint(0, 90)
    return inicio + timedelta(days=delta)


class Command(BaseCommand):
    help = (
        'Popula o banco de dados com categorias e movimentações de exemplo. '
        'Deve ser executado uma única vez durante a configuração inicial.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            default=None,
            help='Username do usuário para associar os dados. Se não informado, usa o primeiro superusuário.',
        )

    def handle(self, *args, **options):
        usuario = self._obter_usuario(options['usuario'])
        if not usuario:
            return

        self.stdout.write(f'Populando dados para o usuário: {usuario.username}')

        categorias = self._criar_categorias(usuario)
        self._criar_movimentacoes_pontuais(usuario, categorias)
        self._criar_movimentacoes_recorrentes(usuario, categorias)

        self.stdout.write(self.style.SUCCESS('Seed concluído com sucesso!'))

    def _obter_usuario(self, username):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f'Usuário "{username}" não encontrado. Crie o usuário antes de executar o seed.'
                ))
                return None

        usuario = User.objects.filter(is_superuser=True).first()
        if not usuario:
            usuario = User.objects.first()
        if not usuario:
            self.stderr.write(self.style.ERROR(
                'Nenhum usuário encontrado. Crie um usuário antes de executar o seed.'
            ))
            return None
        return usuario

    def _criar_categorias(self, usuario):
        categorias = {}

        for cat_data in CATEGORIAS_DESPESA + CATEGORIAS_RECEITA:
            cat, created = Categoria.objects.get_or_create(
                usuario=usuario,
                nome=cat_data['nome'],
                defaults={
                    'cor': cat_data['cor'],
                    'icone': cat_data['icone'],
                },
            )
            categorias[cat_data['nome']] = cat
            status = 'criada' if created else 'já existia'
            self.stdout.write(f'  Categoria "{cat.nome}" — {status}')

        return categorias

    def _criar_movimentacoes_pontuais(self, usuario, categorias):
        novas = []

        for config in MOVIMENTACOES_DESPESA:
            novas.append(Movimentacao(
                usuario=usuario,
                categoria=categorias[config['categoria']],
                descricao=config['descricao'],
                valor=_gerar_valor(config),
                tipo='despesa',
                data=_data_aleatoria_ultimo_trimestre(),
            ))

        for config in MOVIMENTACOES_RECEITA:
            novas.append(Movimentacao(
                usuario=usuario,
                categoria=categorias[config['categoria']],
                descricao=config['descricao'],
                valor=_gerar_valor(config),
                tipo='receita',
                data=_data_aleatoria_ultimo_trimestre(),
            ))

        Movimentacao.objects.bulk_create(novas)
        self.stdout.write(f'  {len(novas)} movimentações pontuais criadas.')

    def _criar_movimentacoes_recorrentes(self, usuario, categorias):
        hoje = date.today()
        data_limite = hoje + timedelta(days=180)

        recorrentes = [
            {
                'categoria': 'Moradia',
                'descricao': 'Aluguel - Recorrente',
                'valor': Decimal('1200.00'),
                'tipo': 'despesa',
                'frequencia': 'mensal',
                'dia_mes': 5,
            },
            {
                'categoria': 'Alimentação',
                'descricao': 'Alimentação - Recorrente',
                'valor': Decimal(str(random.randint(100, 500))),
                'tipo': 'despesa',
                'frequencia': 'semanal',
                'dias_semana': '0',
            },
            {
                'categoria': 'Salário',
                'descricao': 'Salário - Recorrente',
                'valor': Decimal('3000.00'),
                'tipo': 'receita',
                'frequencia': 'mensal',
                'dia_mes': 1,
            },
            {
                'categoria': 'Freelance',
                'descricao': 'Freelance - Recorrente',
                'valor': Decimal(str(random.randint(200, 1000))),
                'tipo': 'receita',
                'frequencia': 'semanal',
                'dias_semana': '4',
            },
        ]

        for config in recorrentes:
            Movimentacao.objects.create(
                usuario=usuario,
                categoria=categorias[config['categoria']],
                descricao=config['descricao'],
                valor=config['valor'],
                tipo=config['tipo'],
                data=hoje,
                recorrente=True,
                frequencia=config['frequencia'],
                dias_semana=config.get('dias_semana'),
                dia_mes=config.get('dia_mes'),
                data_limite=data_limite,
            )
            self.stdout.write(
                f'  Recorrência criada: {config["descricao"]} ({config["frequencia"]})'
            )

        self.stdout.write(f'  {len(recorrentes)} movimentações recorrentes criadas.')
