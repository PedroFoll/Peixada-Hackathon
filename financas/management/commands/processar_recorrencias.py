from django.core.management.base import BaseCommand

from financas.models import Movimentacao
from financas.services import gerar_movimentacoes_recorrentes


class Command(BaseCommand):
    help = 'Processa movimentações recorrentes e gera as ocorrências futuras pendentes.'

    def handle(self, *args, **options):
        recorrentes = Movimentacao.objects.filter(recorrente=True).select_related('categoria')
        total_criadas = 0

        for mov in recorrentes:
            criadas = gerar_movimentacoes_recorrentes(mov)
            if criadas:
                self.stdout.write(
                    f'  {mov}: {criadas} ocorrência(s) gerada(s)'
                )
                total_criadas += criadas

        self.stdout.write(
            self.style.SUCCESS(f'Concluído: {total_criadas} movimentação(ões) criada(s).')
        )
