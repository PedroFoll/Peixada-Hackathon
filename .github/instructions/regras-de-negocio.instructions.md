---
description: >
  Regras de negócio do sistema de monitoramento de finanças pessoais.
  Aplicar em toda implementação de models, views, forms, services, templates e JavaScript
  relacionados a movimentações financeiras, categorias, dashboard e perfil de usuário.
applyTo: "**/*.py, **/*.html, **/*.js"
---

# Regras de Negócio — Sistema de Finanças Pessoais

## 1. Movimentações (Receitas e Despesas)

### 1.1 Tipos de Movimentação
- Toda movimentação é classificada como **receita** ou **despesa**.
- Toda movimentação pertence a **um único usuário** — nunca expor dados de outros usuários.
- O campo **valor** deve ser sempre positivo e usar `DecimalField` (nunca `FloatField`).
- O campo **descrição** é **opcional**.
- A **categoria** é obrigatória para toda movimentação.
- A **data** é obrigatória e deve ser validada (não pode ser nula ou em formato inválido).

### 1.2 Movimentações Recorrentes
- Uma movimentação pode ser **pontual** ou **recorrente**.
- Quando recorrente, o usuário deve escolher a **frequência**:
  - `diaria` — repete todos os dias
  - `semanal` — repete em dias específicos da semana (0=Segunda … 6=Domingo); pelo menos 1 dia obrigatório
  - `mensal` — repete em um dia específico do mês (1–31)
- O campo **data_limite** define quando a recorrência encerra (opcional; sem data limite = recorrência indefinida).
- Recorrências geram instâncias de movimentação automaticamente via `services.py` — nunca na view.
- Uma movimentação recorrente não pode ter frequência nula: se `recorrente=True`, `frequencia` é obrigatório.

### 1.3 Validações de Movimentação
- `valor` deve ser maior que zero.
- Para movimentação recorrente `semanal`, `dias_semana` deve conter ao menos 1 dia válido.
- Para movimentação recorrente `mensal`, `dia_mes` deve estar entre 1 e 31.
- `data_limite` (quando informada) não pode ser anterior à `data` da movimentação.
- Validações implementadas em `clean()` ou `clean_<campo>()` no `forms.py` — nunca na view.

---

## 2. Categorias

### 2.1 Comportamento
- Categorias pertencem a um **usuário** (cada usuário gerencia suas próprias categorias).
- O nome da categoria deve ser **único por usuário** (combinação `usuario + nome`).
- Categorias são usadas tanto para despesas quanto para receitas.

### 2.2 Exclusão de Categorias — Regra Crítica
- **NÃO é permitido excluir** uma categoria que possua movimentações (receitas ou despesas) vinculadas.
- Ao tentar excluir, verificar via ORM se existem movimentações associadas:
  ```python
  if categoria.movimentacoes.exists():
      messages.error(request, "Categoria não pode ser excluída pois possui movimentações vinculadas.")
      return redirect(...)
  ```
- Categorias **sem** movimentações podem ser excluídas livremente.
- Categorias **com** movimentações **só podem ser editadas** (nome).
- A verificação de vinculação deve ocorrer na `view` antes de chamar `.delete()`, envolto em `try/except`.

### 2.3 Interface de Categorias
- Criação e edição de categorias via **modal** (nunca pages separadas).
- O modal deve exibir claramente se a categoria já possui movimentações (desativar botão de exclusão).

---

## 3. Dashboard

### 3.1 Gráficos Obrigatórios
O dashboard deve conter os seguintes gráficos usando **Chart.js 4.4**:

| Gráfico | Tipo sugerido | Filtros disponíveis |
|---|---|---|
| Receitas ao longo do tempo | Line / Bar | Diário, Semanal, Mensal, Período |
| Despesas ao longo do tempo | Line / Bar | Diário, Semanal, Mensal, Período |
| Receitas por categoria | Donut / Pie | Período selecionado |
| Despesas por categoria | Donut / Pie | Período selecionado |
| Comparação Receita × Despesa | Grouped Bar | Diário, Semanal, Mensal, Período |

### 3.2 Dados para Gráficos — Regra de Segurança (XSS)
- Dados do Django **nunca** são interpolados diretamente em `<script>`:
  ```html
  <!-- CORRETO -->
  <div id="chart-data"
       data-labels="{{ labels|escapejs }}"
       data-receitas="{{ valores_receitas|escapejs }}"
       data-despesas="{{ valores_despesas|escapejs }}">
  </div>

  <!-- ERRADO — vulnerável a XSS -->
  <script>
    const labels = {{ labels }};
  </script>
  ```
- O JavaScript lê os valores via `dataset` do elemento DOM.
- Todos os dados passados via `data-*` devem ser serializados com `json.dumps` + `|safe` no contexto da view.

### 3.3 Filtros do Dashboard
- Filtro de período: `diario`, `semanal`, `mensal`, `personalizado` (data início + data fim).
- Para período personalizado, `data_inicio` não pode ser após `data_fim`.
- Filtros transmitidos via `GET` — sem alteração de estado no servidor ao filtrar.
- Período padrão ao carregar: **mês atual**.

---

## 4. Tela de Lançamentos (Tabela de Movimentações)

### 4.1 Colunas Obrigatórias
A tabela deve exibir:
- **Descrição** (pode estar vazia — exibir "—" quando ausente)
- **Valor** (formatado em moeda: `R$ 1.234,56`)
- **Categoria**
- **Data** (formato `DD/MM/YYYY`)
- **Tipo** (receita / despesa) — com diferenciação visual (cor verde para receita, vermelho para despesa)
- **Recorrente** (ícone indicativo)

### 4.2 Filtros da Tabela
Filtros disponíveis (via `GET`):
- `data_inicio` e `data_fim` — intervalo de datas
- `categoria` — por ID de categoria
- `descricao` — busca textual (case-insensitive, `icontains`)
- `tipo` — `receita` ou `despesa`

### 4.3 Exclusão de Movimentações
- Exclusão sempre exige **confirmação via modal** antes de executar.
- O modal deve exibir a descrição e o valor da movimentação a ser excluída.
- A view de exclusão aceita apenas `POST` — GET não deve excluir nada.
- Usar `messages.success` / `messages.error` após a operação.

---

## 5. Menu Lateral

O menu lateral deve conter **obrigatoriamente** os seguintes itens de navegação:

| Item | URL destino | Ícone Bootstrap Icons |
|---|---|---|
| Dashboard | `dashboard:index` | `bi-speedometer2` |
| Lançamentos | `financas:lancamentos` | `bi-list-ul` |
| Categorias | `financas:categorias` | `bi-tags` |
| Perfil | `usuarios:perfil` | `bi-person-circle` |
| Sair | `usuarios:logout` | `bi-box-arrow-right` |

- O item ativo deve ser destacado visualmente com a classe `active`.
- O menu deve ser responsivo: colapsável em telas menores que `md` (768px).

---

## 6. Autenticação e Perfil

### 6.1 Regras de Autenticação
- Todas as views (exceto login) protegidas por `LoginRequiredMixin`.
- Redirecionamento após login: `dashboard:index`.
- Redirecionamento após logout: página de login.
- Usuário não autenticado redirecionado automaticamente para `LOGIN_URL`.

### 6.2 Perfil do Usuário
O usuário pode editar:
- **Nome** (`first_name` + `last_name`)
- **Email** (único no sistema — validar unicidade no `clean_email()`)
- **Senha** (apenas via formulário de troca de senha separado, usando `PasswordChangeForm` do Django)

Campos **não editáveis** pelo usuário: `username`, `date_joined`.

### 6.3 Troca de Senha
- Usar `PasswordChangeForm` nativo do Django.
- Após troca bem-sucedida, re-autenticar o usuário com `update_session_auth_hash`.
- Exibir `messages.success` após alteração.

---

## 7. Modais — Padrão de Interface

Todos os modais de cadastro/edição devem seguir Este padrão:

```html
<!-- Botão que abre o modal -->
<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalCadastro">
  <i class="bi bi-plus-lg me-1"></i>Novo
</button>

<!-- Modal -->
<div class="modal fade" id="modalCadastro" tabindex="-1" aria-labelledby="modalCadastroLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modalCadastroLabel">Título do Modal</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
      </div>
      <form method="post" action="{% url 'nome_da_url' %}">
        {% csrf_token %}
        <div class="modal-body">
          <!-- Campos do formulário -->
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Cancelar</button>
          <button type="submit" class="btn btn-primary">Salvar</button>
        </div>
      </form>
    </div>
  </div>
</div>
```

### 7.1 Modal de Cadastro de Despesa/Receita — Campos Obrigatórios
- Tipo (receita / despesa)
- Categoria (select com categorias do usuário)
- Valor (`DecimalField`, positivo)
- Data
- Descrição (opcional)
- Checkbox "É recorrente?"
- **Quando recorrente marcado**, exibir (via JavaScript `show/hide`):
  - Select de frequência: `diaria`, `semanal`, `mensal`
  - Para `semanal`: checkboxes dos dias da semana (Seg, Ter, Qua, Qui, Sex, Sáb, Dom)
  - Para `mensal`: select com dias 1–31
  - Campo de data limite (opcional)

### 7.2 Modal de Exclusão — Padrão Obrigatório
- Nunca excluir via GET ou clique direto.
- Modal de confirmação com nome/descrição do item.
- Form dentro do modal com `method="post"` e `{% csrf_token %}`.
- Botão "Excluir" com classe `btn-danger`.

---

## 8. Segurança — Regras Invioláveis

- `get_object_or_404(Model, pk=pk, usuario=request.user)` em toda busca por PK.
- Nunca retornar dados de outros usuários — todo `queryset` deve filtrar por `request.user`.
- Nunca interpolar variáveis Python diretamente em `<script>` — usar atributos `data-*`.
- `{% csrf_token %}` em todo `<form method="post">`.
- Senhas gerenciadas exclusivamente pelo sistema de auth do Django.
- `X_FRAME_OPTIONS = 'DENY'` e `SECURE_CONTENT_TYPE_NOSNIFF = True` no `settings.py`.

---

## 9. Formatação e UX

- Valores monetários formatados como `R$ 1.234,56` em toda a interface.
- Datas exibidas no formato `DD/MM/YYYY`.
- Receitas: cor **verde** (`text-success` / `#198754`).
- Despesas: cor **vermelha** (`text-danger` / `#dc3545`).
- Feedback de operações via `messages` do Django — renderizados no `base.html`.
- Tabelas com paginação quando ultrapassar **20 registros por página**.
