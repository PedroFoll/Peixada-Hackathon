from django import forms

from .models import Categoria, Movimentacao

DIAS_SEMANA_CHOICES = [
    ('0', 'Seg'),
    ('1', 'Ter'),
    ('2', 'Qua'),
    ('3', 'Qui'),
    ('4', 'Sex'),
    ('5', 'Sáb'),
    ('6', 'Dom'),
]


class MovimentacaoForm(forms.ModelForm):
    dias_semana = forms.MultipleChoiceField(
        choices=DIAS_SEMANA_CHOICES,
        required=False,
        label='Dias da semana',
    )

    class Meta:
        model = Movimentacao
        fields = [
            'tipo', 'categoria', 'valor', 'data', 'descricao',
            'recorrente', 'frequencia', 'dias_semana', 'dia_mes', 'data_limite',
        ]
        widgets = {
            'tipo': forms.HiddenInput(),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0.01',
            }),
            'data': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'descricao': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Descrição (opcional)',
            }),
            'recorrente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'frequencia': forms.Select(attrs={'class': 'form-select'}),
            'dia_mes': forms.NumberInput(attrs={
                'class': 'form-control', 'min': '1', 'max': '31',
            }),
            'data_limite': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d',
            ),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)
        else:
            self.fields['categoria'].queryset = Categoria.objects.none()
        self.fields['categoria'].empty_label = 'Selecione uma categoria'
        self.fields['frequencia'].required = False
        # Pre-fill dias_semana for edit forms (model stores as "0,2,4" string)
        instance = kwargs.get('instance')
        if instance and instance.dias_semana:
            self.fields['dias_semana'].initial = instance.dias_semana.split(',')

    def clean_dias_semana(self):
        dias = self.cleaned_data.get('dias_semana') or []
        return ','.join(dias) if dias else None

    def clean(self):
        cleaned = super().clean()
        valor = cleaned.get('valor')
        recorrente = cleaned.get('recorrente')
        frequencia = cleaned.get('frequencia')
        dias_semana = cleaned.get('dias_semana')
        dia_mes = cleaned.get('dia_mes')
        data = cleaned.get('data')
        data_limite = cleaned.get('data_limite')

        if valor is not None and valor <= 0:
            self.add_error('valor', 'O valor deve ser maior que zero.')

        if recorrente:
            if not frequencia:
                self.add_error('frequencia', 'Frequência é obrigatória para movimentações recorrentes.')
            elif frequencia == 'semanal' and not dias_semana:
                self.add_error('dias_semana', 'Selecione ao menos um dia da semana.')
            elif frequencia == 'mensal':
                if not dia_mes:
                    self.add_error('dia_mes', 'Informe o dia do mês para recorrência mensal.')
                elif not (1 <= dia_mes <= 31):
                    self.add_error('dia_mes', 'O dia do mês deve estar entre 1 e 31.')

        if data and data_limite and data_limite < data:
            self.add_error('data_limite', 'A data limite não pode ser anterior à data da movimentação.')

        return cleaned


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'cor', 'icone']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: Alimentação',
            }),
            'cor': forms.TextInput(attrs={
                'class': 'form-control form-control-color', 'type': 'color',
            }),
            'icone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: bi-cart',
            }),
        }
