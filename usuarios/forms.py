from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


class CadastroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
        })
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label='Nome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome',
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label='Sobrenome',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'nome_usuario',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email


class PerfilForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label='Sobrenome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        return email


class AlterarSenhaForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['old_password'].help_text = None
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None
