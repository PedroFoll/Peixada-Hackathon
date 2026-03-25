from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categorias')
    nome = models.CharField(max_length=100)
    cor = models.CharField(max_length=7, default='#6c757d', blank=True)
    icone = models.CharField(max_length=50, default='bi-tag', blank=True)

    class Meta:
        unique_together = [['usuario', 'nome']]
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]
    FREQUENCIA_CHOICES = [
        ('diaria', 'Diária'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movimentacoes')
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, related_name='movimentacoes'
    )
    descricao = models.CharField(max_length=255, blank=True, default='')
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, db_index=True)
    data = models.DateField(db_index=True)
    recorrente = models.BooleanField(default=False)
    frequencia = models.CharField(
        max_length=10, choices=FREQUENCIA_CHOICES, null=True, blank=True
    )
    dias_semana = models.CharField(max_length=20, null=True, blank=True)
    dia_mes = models.PositiveSmallIntegerField(null=True, blank=True)
    data_limite = models.DateField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'data', 'tipo']),
        ]

    def __str__(self):
        desc = self.descricao or 'Sem descrição'
        return f'{self.get_tipo_display()}: {desc} (R$ {self.valor})'
