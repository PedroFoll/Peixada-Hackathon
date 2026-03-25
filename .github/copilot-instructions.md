# Instruções Globais do Projeto — Peixada Hackathon

Este projeto é uma aplicação web de **gestão financeira pessoal** desenvolvida com **Django 5.1**, **Python 3.13**, **SQLite**, **Bootstrap 5** e **Chart.js**, com renderização server-side via templates Django.

---

## Stack e Restrições Absolutas

| Tecnologia | Versão | Status |
|------------|--------|--------|
| Python | 3.13 | ✅ Obrigatório |
| Django | 5.1 | ✅ Obrigatório |
| SQLite | nativo | ✅ Obrigatório |
| Bootstrap | 5.3 | ✅ Obrigatório |
| Chart.js | 4.4 | ✅ Obrigatório |
| Docker / Containers | qualquer | ❌ PROIBIDO |
| Django REST Framework | qualquer | ❌ PROIBIDO |
| Frameworks JS (React, Vue, Angular) | qualquer | ❌ PROIBIDO |
| Cache de página / template | qualquer | ❌ PROIBIDO (dados mudam frequentemente) |
| SQL bruto com f-string / concatenação | — | ❌ PROIBIDO (SQL injection) |

---

## Arquitetura — Regras Estruturais

- Apps organizados por domínio de negócio (ex: `financas`, `usuarios`, `relatorios`)
- Separação obrigatória de responsabilidades:
  - `models.py` → estrutura de dados
  - `views.py` → orquestração (sem lógica de negócio)
  - `services.py` → lógica de negócio
  - `forms.py` → validação de entrada
  - `urls.py` → roteamento com `name=` em todos os endpoints
  - `templates/` → renderização HTML
  - `management/commands/` → comandos personalizados
- Toda interação com o usuário acontece via views que renderizam templates HTML — sem APIs REST
- `SECRET_KEY` sempre em variável de ambiente — nunca hardcoded no código-fonte

---

## Segurança — Regras Obrigatórias

- Todas as views com dados do usuário protegidas por `LoginRequiredMixin`
- Dados sempre filtrados por `request.user` — nunca expor dados de outros usuários
- `get_object_or_404(Model, pk=pk, usuario=request.user)` para busca por PK
- `{% csrf_token %}` em todo `<form method="post">`
- `X_FRAME_OPTIONS = 'DENY'` e `SECURE_CONTENT_TYPE_NOSNIFF = True` no `settings.py`
- Senhas gerenciadas exclusivamente pelo sistema de auth do Django
- Queries ao banco sempre via ORM ou parâmetros bind — nunca concatenação de strings

---

## Banco de Dados (SQLite)

- `DecimalField` para valores monetários — **nunca `FloatField`**
- `db_index=True` em campos usados frequentemente em filtros (`data`, `tipo`, `usuario`)
- `select_related()` em todo acesso a `ForeignKey` / `OneToOneField`
- `prefetch_related()` em todo acesso a `ManyToManyField` / reverse FK
- Totais e somas com `aggregate()` / `annotate()` no banco — nunca em loops Python
- Migrações geradas e aplicadas após toda alteração em models

---

## Frontend — Regras Obrigatórias

- HTML semântico: `<main>`, `<nav>`, `<section>`, `<article>`, `<footer>`
- Todo `<img>` com `alt` descritivo; todo `<input>` com `<label>` associado
- CSS mobile-first com variáveis CSS (`--var`) — sem valores hardcoded repetidos
- Layouts com Flexbox ou CSS Grid — nunca `float`
- `{% url 'nome' %}` em todos os links — nunca URLs hardcoded nos templates
- **Todo CSS de página em arquivo externo** (`<app>/static/<app>/css/style.css`) — nunca `<style>` inline em `{% block extra_css %}`
- Dados Django passados ao JavaScript via atributos `data-*` — nunca interpolação direta no script (XSS)

---

## Exclusão de Dados — Padrão Obrigatório

Toda ação de exclusão **exige confirmação via modal** antes de executar. Nunca submeter form de exclusão diretamente ao clicar no botão:

1. Botão na listagem abre modal com `data-bs-toggle="modal"`
2. Form de exclusão fica dentro do modal (com `{% csrf_token %}`)
3. Modal identifica claramente o item (nome/descrição) via `data-nome`
4. View de exclusão aceita apenas `POST` — envolve `.delete()` em `try/except`
5. `messages.success` em caso de sucesso; `messages.error` em caso de falha

---

## Tratamento de Erros HTTP

- Usuário **não autenticado** → redirecionado automaticamente para `LOGIN_URL` pelo `LoginRequiredMixin`
- Usuário **autenticado** acessando página inexistente → exibe template `404.html` customizado (`handler404`)

---

## Formulários

- Sempre `ModelForm` para formulários baseados em modelos
- Validações em `clean()` ou `clean_<campo>()` — nunca na view
- Campos gerenciados pelo sistema (`usuario`, `criado_em`) excluídos do formulário
- Widgets com classes Bootstrap (`form-control`, `form-select`) definidos no `forms.py`
- `usuario` atribuído na view após `form.is_valid()` com `commit=False`

---

## Feedback ao Usuário

- Toda view de criar/editar usa `messages.success` / `messages.error` após operação
- Mensagens renderizadas pelo `base.html` via `{% include "partials/messages.html" %}`
- Mapeamento de tags em `settings.py`: `messages.ERROR → 'danger'`, `messages.SUCCESS → 'success'`

---

## Testes

- `TestCase` do Django para todos os testes (isolamento com banco de dados de teste)
- Cobertura obrigatória: autenticação, isolamento de dados entre usuários, validações de form, cálculos financeiros
- Views de exclusão testadas com GET (não deve excluir) e POST (deve excluir)

---

## Skills Disponíveis

Use as skills abaixo invocando-as no chat conforme o contexto:

| Situação | Skill a invocar |
|----------|----------------|
| Criar/revisar modelos, views, forms, urls, migrações | `software-engineer` |
| Projetar arquitetura, schema de banco, decisões técnicas | `software-architecture` |
| Criar páginas HTML, CSS, Bootstrap, JavaScript, Chart.js | `frontend-developer` |
| Segurança, performance de queries, logs, testes backend | `backend-developer` |
| Gerar README.md ou documento de arquitetura | `documentation-specialist` ou `create-readme` |
| Revisar o projeto completo antes da banca | `/project-review` |
