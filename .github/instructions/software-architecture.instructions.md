
name: software-architecture
description: >
  Skill especializada em arquitetura de software backend utilizando **Django 5.1**, **Python 3.13**, **SQLite**, 
  e **Bootstrap 5**. NÃO UTILIZE **Docker**, **containers**, ou **Django REST Framework**. A arquitetura foca 
  no desenvolvimento de sistemas escaláveis, seguros e manuteníveis com essas tecnologias.
applyTo: "**/*.py,**/models.py,**/views.py,**/urls.py,**/settings.py,**/templates/**/*.html"
---

## Requisitos e Tecnologia

1. **Tecnologias Permitidas**:
   - **Django 5.1**: Framework para desenvolvimento backend em Python.
   - **Python 3.13**: Versão de Python para garantir compatibilidade com Django e outros pacotes.
   - **SQLite**: Banco de dados relacional para armazenamento de dados.
   - **Bootstrap 5**: Framework front-end para construção de layouts responsivos e elegantes.

2. **Tecnologias NÃO Permitidas**:
   - **Docker**: Não deve ser utilizado para empacotar a aplicação.
   - **Containers**: Não usar tecnologias de containers como Kubernetes, Docker Compose, etc.
   - **Django REST Framework**: A arquitetura deve ser implementada sem a necessidade de construir APIs RESTful.

---

## Arquitetura do Sistema

### 1. **Configuração do Projeto Django**
   - Inicie o projeto com o Django 5.1, utilizando o Python 3.13.
   - Aplique a configuração do **SQLite** como banco de dados padrão.

```bash
# Criar ambiente virtual e ativar
python -m venv venv
venv\Scripts ctivate  # Windows
pip install django==5.1

# Criar o projeto e o primeiro app
django-admin startproject core .
python manage.py startapp financeiro
```

### 2. **Estrutura de Diretórios**
   A estrutura do projeto deve ser organizada da seguinte forma:
```
/core/
    manage.py
    /core/
        settings.py
        urls.py
        wsgi.py
    /financeiro/
        models.py
        views.py
        urls.py
        /templates/
            /financeiro/
                index.html
                dashboard.html
        /static/
            /css/
                style.css
```

- **`/financeiro/`**: Aplicação que gerencia todos os aspectos financeiros, incluindo receitas e despesas.
- **`/templates/`**: Contém os arquivos HTML do sistema, utilizando o **Bootstrap 5** para o design responsivo.
- **`/static/`**: Contém arquivos estáticos como CSS personalizados.

---

### 3. **Configuração do Banco de Dados (SQLite)**

- **Banco de Dados SQLite**: Utilizando o banco relacional SQLite para persistência de dados.

```python
# settings.py (configuração do banco de dados)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

### 4. **Desenvolvimento de Models e Views**

- **Models**: Os modelos devem ser criados no arquivo **models.py** dentro de cada aplicativo, utilizando os tipos de campo adequados para receitas e despesas.

```python
# models.py
from django.db import models

class Receita(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()

    def __str__(self):
        return self.descricao

class Despesa(models.Model):
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()

    def __str__(self):
        return self.descricao
```

- **Views**: Criação de views que renderizam templates HTML, usando o Django **Template Language (DTL)** para exibição de dados.

```python
# views.py
from django.shortcuts import render
from .models import Receita, Despesa

def dashboard(request):
    receitas = Receita.objects.all()
    despesas = Despesa.objects.all()
    saldo = sum([r.valor for r in receitas]) - sum([d.valor for d in despesas])

    return render(request, 'financeiro/dashboard.html', {'receitas': receitas, 'despesas': despesas, 'saldo': saldo})
```

---

### 5. **Templates HTML com Bootstrap 5**

Os templates HTML devem usar o **Bootstrap 5** para construção de layouts responsivos. O Bootstrap será incluído nos arquivos **HTML** diretamente.

```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Gestão Financeira</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Dashboard de Gestão Financeira</h1>
        <div class="row">
            <div class="col-md-6">
                <h3>Receitas</h3>
                <ul class="list-group">
                    {% for receita in receitas %}
                    <li class="list-group-item">{{ receita.descricao }} - R$ {{ receita.valor }}</li>
                    {% endfor %}
                </ul>
            </div>
            <div class="col-md-6">
                <h3>Despesas</h3>
                <ul class="list-group">
                    {% for despesa in despesas %}
                    <li class="list-group-item">{{ despesa.descricao }} - R$ {{ despesa.valor }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        <h3 class="mt-4">Saldo: R$ {{ saldo }}</h3>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

### 6. **Configuração das URLs**

- Defina as URLs para renderizar os templates, como o **dashboard** para exibir a visão geral das finanças.

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
```

---

### 7. **Segurança e Manutenção**

- **Segurança**: Proteja os dados financeiros sensíveis, como senhas e transações.
- **Manutenção**: Utilize o Django **migrations** para manter a consistência do banco de dados ao longo do tempo.

```bash
# Executando migrações
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations   # verificar estado
```

---

### 8. **Testes**

- Criação de testes para garantir que a lógica de negócios e a interface de usuário estejam funcionando corretamente.

```python
# tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from .models import Receita, Despesa

class DashboardTest(TestCase):

    def setUp(self):
        Receita.objects.create(descricao='Salário', valor=1000.00, data='2023-04-01')
        Despesa.objects.create(descricao='Aluguel', valor=500.00, data='2023-04-01')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Salário')
        self.assertContains(response, 'Aluguel')
        self.assertContains(response, 'Saldo')
```

---

### 9. **Comandos de Referência Rápida**

```bash
# Iniciar servidor de desenvolvimento
python manage.py runserver

# Criar superusuário
python manage.py createsuperuser

# Executar todos os testes
pytest

# Verificar desvio de migrações
python manage.py migrate --check

# Inspecionar banco de dados SQLite
python manage.py dbshell
```

