from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from financas.models import Categoria, Movimentacao


class Command(BaseCommand):
    help = (
        'Remove todas as movimentações e categorias de um usuário. '
        'Útil para limpar dados de seed antes de repopular.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            default=None,
            help='Username do usuário cujos dados serão removidos. Se não informado, usa o primeiro superusuário.',
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão sem pedir interação no terminal.',
        )

    def handle(self, *args, **options):
        usuario = self._obter_usuario(options['usuario'])
        if not usuario:
            return

        total_mov = Movimentacao.objects.filter(usuario=usuario).count()
        total_cat = Categoria.objects.filter(usuario=usuario).count()

        if total_mov == 0 and total_cat == 0:
            self.stdout.write(self.style.WARNING(
                f'Nenhum dado encontrado para o usuário "{usuario.username}".'
            ))
            return

        self.stdout.write(
            f'Usuário: {usuario.username}\n'
            f'  Movimentações a remover: {total_mov}\n'
            f'  Categorias a remover: {total_cat}'
        )

        if not options['confirmar']:
            resposta = input('\nTem certeza que deseja excluir todos os dados? (s/N): ')
            if resposta.strip().lower() != 's':
                self.stdout.write(self.style.WARNING('Operação cancelada.'))
                return

        mov_deletadas, _ = Movimentacao.objects.filter(usuario=usuario).delete()
        cat_deletadas, _ = Categoria.objects.filter(usuario=usuario).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Limpeza concluída: {mov_deletadas} movimentação(ões) e '
            f'{cat_deletadas} categoria(s) removida(s).'
        ))

    def _obter_usuario(self, username):
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(
                    f'Usuário "{username}" não encontrado.'
                ))
                return None

        usuario = User.objects.filter(is_superuser=True).first()
        if not usuario:
            usuario = User.objects.first()
        if not usuario:
            self.stderr.write(self.style.ERROR(
                'Nenhum usuário encontrado.'
            ))
            return None
        return usuario
