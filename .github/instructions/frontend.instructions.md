---
description: "Use quando: desenvolver páginas web, componentes HTML, CSS, JavaScript ou Bootstrap. Aplica padrões de qualidade, semântica, acessibilidade e boas práticas frontend."
applyTo: "**/*.html, **/*.css, **/*.js"
---

# Padrões de Desenvolvimento Frontend

## HTML — Estrutura Semântica

- Use tags semânticas: `<header>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`, `<nav>`
- Nunca use `<div>` onde uma tag semântica existe
- Todo `<img>` deve ter atributo `alt` descritivo
- Inputs de formulário sempre com `<label>` associado via `for`/`id`
- Use `<button>` para ações e `<a>` para navegação — nunca ao contrário
- Coloque `<link>` de CSS no `<head>` e `<script>` antes do `</body>`
- Use atributos `aria-*` e `role` para acessibilidade
- Prefira atributos `data-*` para guardar dados no DOM

## CSS — Estilização e Layout

- Use **variáveis CSS** (`--var`) para cores, fontes e espaçamentos — nunca valores hardcoded repetidos
- **Mobile-first**: comece o estilo pela versão mobile, expanda com `@media (min-width: ...)`
- Evite `!important` — resolva especificidade na estrutura do CSS
- Prefira classes a IDs para estilização
- Use sistema de espaçamento múltiplo de 8px (4, 8, 12, 16, 24, 32, 48, 64px)
- Organize o CSS em seções comentadas: `/* === SEÇÃO === */`
- Prefira `rem` para tipografia e `px` para bordas/sombras

## JavaScript — Interatividade

- Use `const` por padrão; `let` somente quando reatribuição for necessária; **nunca `var`**
- Prefira funções com nomes descritivos e responsabilidade única
- Use `addEventListener` em vez de atributos `onclick` inline no HTML
- Valide dados antes de manipular o DOM
- Trate erros de `fetch` com `try/catch` e exiba feedback ao usuário
- Separe responsabilidades em arquivos: `main.js`, `charts.js`, `utils.js`
- Use `textContent` para inserir texto dinâmico — nunca `innerHTML` com dados externos (XSS)

## Bootstrap 5 — Responsividade

- Sempre importe o Bootstrap antes do CSS customizado
- Use o grid de 12 colunas com classes responsivas: `col-12 col-md-6 col-lg-4`
- Prefira utilitários Bootstrap (`d-flex`, `gap-3`, `mt-4`) a criar classes CSS equivalentes
- Sobrescreva variáveis Bootstrap via CSS custom properties quando precisar customizar o tema
- Não misture grid Bootstrap com CSS Grid/Flexbox custom no mesmo elemento

## Acessibilidade (WCAG 2.1 AA)

- Contraste mínimo de 4.5:1 para texto normal; 3:1 para texto grande e elementos UI
- Não use cor como único meio de transmitir informação
- Todos os elementos interativos precisam de foco visível (`:focus-visible`)
- Textos alternativos descritivos para todas as imagens e ícones
- Navegação por teclado funcional em todos os componentes interativos

## Organização de Arquivos

### Partials (componentes globais)

Cada componente da interface (**partial**) é uma pasta autossuficiente dentro de `templates/partials/`.
Todo o HTML, CSS, JS e imagens de um componente ficam co-localizados dentro da pasta do componente.

```
templates/
├── base.html               ← layout raiz; carrega CSS/JS de todos os componentes
└── partials/
    └── <componente>/
        ├── <componente>.html           ← template do componente
        └── static/
            └── <componente>/           ← namespaced para evitar conflitos
                ├── css/
                │   └── <componente>.css
                ├── js/
                │   └── <componente>.js
                └── images/
```

**Exemplo concreto:**
```
templates/partials/sidebar/
├── sidebar.html
└── static/
    └── sidebar/
        ├── css/sidebar.css
        ├── js/sidebar.js
        └── images/
```

**Regras desta estrutura:**
- CSS e JS globais (variáveis, reset, layout) ficam em `static/css/styles.css` e `static/js/main.js`
- CSS e JS específicos de um componente ficam **dentro** da pasta do componente
- O namespacing (`static/<componente>/`) é obrigatório para evitar colisões no `collectstatic`
- O `base.html` carrega os arquivos do componente com `{% static '<componente>/css/<componente>.css' %}`
- O Django descobre automaticamente as pastas `static/` dos componentes via `_discover_component_statics()` em `settings.py`
- Ao criar um novo componente, **não é necessário** editar `settings.py` — a descoberta é automática

### Apps Django (pages/)

Cada app em `pages/` que possui templates deve ter seus estilos em um arquivo CSS dedicado:

```
pages/<app>/
├── static/
│   └── <app>/
│       └── css/
│           └── style.css   ← todos os estilos das páginas do app (lista, form, etc.)
└── templates/
    └── <app>/
        └── *.html          ← templates referenciam o CSS externo via <link>
```

**Regras obrigatórias:**
- **Nunca use `<style>` inline dentro de `{% block extra_css %}`** — todo CSS de página vai em `<app>/static/<app>/css/style.css`
- No bloco `{% block extra_css %}` use apenas `<link rel="stylesheet">`, nunca `<style>...</style>`
- Os templates referenciam o arquivo via `{% static '<app>/css/style.css' %}`
- Organize o CSS em seções comentadas por template: `/* === LISTA === */`, `/* === FORMULÁRIO === */`
- Estilos compartilhados entre todos os apps ficam em `static/css/styles.css` (global)

**Exemplo correto em um template:**
```html
{% block extra_css %}
<link rel="stylesheet" href="{% static '<app>/css/style.css' %}">
{% endblock %}
```

## Notificações de Feedback (obrigatório)

### Formulários (criar / editar)

- Todo formulário Django **deve exibir mensagens de feedback** após submit usando o sistema de `messages` do Django renderizado no `base.html`
- A view responsável deve usar `messages.success(request, '...')` em caso de sucesso e `messages.error(request, f'...: {e}')` em caso de exceção (com o motivo do erro)
- O template do formulário **não precisa** de notificação extra — as mensagens são exibidas pelo `base.html` após o redirect

### Listagens (excluir linha)

> **OBRIGATÓRIO**: toda ação de exclusão de dados **deve exigir confirmação explícita do usuário** antes de executar o `.delete()`. Nunca submeta um form de exclusão diretamente ao clicar no botão — sempre interponha um modal de confirmação.

- O botão de exclusão **abre um modal de confirmação** via `data-bs-toggle="modal"` — nunca submete o form diretamente.
- O form de exclusão fica **dentro do modal**, não no botão da listagem.
- O modal deve identificar claramente o item que será excluído (nome ou descrição).
- A view de exclusão **deve** envolver o `.delete()` em `try/except Exception as e` e usar:
  - `messages.success(request, '...')` — quando a exclusão ocorrer com sucesso
  - `messages.error(request, f'Erro ao excluir ...: {e}')` — quando ocorrer qualquer falha, informando o motivo

### Padrão de botão de exclusão com confirmação (obrigatório)

```html
<!-- Botão na listagem — apenas abre o modal -->
<button type="button"
        class="btn btn-sm btn-outline-danger"
        title="Excluir"
        data-bs-toggle="modal"
        data-bs-target="#modalExcluir"
        data-id="{{ objeto.pk }}"
        data-nome="{{ objeto }}">
  <i class="bi bi-trash3"></i>
</button>

<!-- Modal de confirmação — colocar uma única vez no template (fora do loop) -->
<div class="modal fade" id="modalExcluir" tabindex="-1" aria-labelledby="modalExcluirLabel" aria-modal="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modalExcluirLabel">Confirmar exclusão</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
      </div>
      <div class="modal-body">
        Tem certeza que deseja excluir <strong id="modalExcluirNome"></strong>?
        <br><small class="text-muted">Esta ação não pode ser desfeita.</small>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <form id="formExcluir" method="post" style="display:inline;">
          {% csrf_token %}
          <button type="submit" class="btn btn-danger">
            <i class="bi bi-trash3 me-1"></i> Excluir
          </button>
        </form>
      </div>
    </div>
  </div>
</div>

<!-- Script: preenche o modal com os dados do item clicado -->
<script>
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('modalExcluir');
  modal.addEventListener('show.bs.modal', (event) => {
    const btn = event.relatedTarget;
    const id   = btn.dataset.id;
    const nome = btn.dataset.nome;
    document.getElementById('modalExcluirNome').textContent = nome;
    document.getElementById('formExcluir').action =
      "{% url '<app>:<excluir>' 0 %}".replace('/0/', `/${id}/`);
  });
});
</script>
```

### Padrão de view de exclusão

```python
def excluir(request, pk):
    if request.method == 'POST':
        obj = get_object_or_404(Model, pk=pk)
        try:
            obj.delete()
            messages.success(request, 'Item excluído com sucesso.')
        except Exception as e:
            messages.error(request, f'Erro ao excluir item: {e}')
    else:
        messages.error(request, 'Método inválido para exclusão.')
    return redirect('<app>:lista')
```

## Performance

- Carregue scripts com `defer` ou posicione antes do `</body>`
- Use imagens com dimensões corretas e formato adequado (WebP quando possível)
- Minimize requisições externas — agrupe CSS e JS quando possível
- Lazy load em imagens fora da viewport: `<img loading="lazy">`