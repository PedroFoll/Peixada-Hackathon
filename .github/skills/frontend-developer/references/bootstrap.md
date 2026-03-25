# Referência Bootstrap 5 — Exemplos e Templates

## Breakpoints

| Prefixo | Largura mínima | Dispositivo |
|---------|---------------|-------------|
| *(sem prefixo)* | < 576px | Mobile |
| `sm` | ≥ 576px | Mobile grande |
| `md` | ≥ 768px | Tablet |
| `lg` | ≥ 992px | Desktop |
| `xl` | ≥ 1200px | Desktop grande |
| `xxl` | ≥ 1400px | Monitor |

## Grid System

```html
<!-- 1 coluna no mobile → 2 no tablet → 3 no desktop -->
<div class="container">
  <div class="row g-4">
    <div class="col-12 col-md-6 col-lg-4">Card 1</div>
    <div class="col-12 col-md-6 col-lg-4">Card 2</div>
    <div class="col-12 col-md-6 col-lg-4">Card 3</div>
  </div>
</div>

<!-- Layout 2/3 + 1/3 (conteúdo + sidebar) -->
<div class="container">
  <div class="row g-4">
    <div class="col-12 col-lg-8">Conteúdo principal</div>
    <div class="col-12 col-lg-4">Sidebar</div>
  </div>
</div>
```

## Navbar Responsiva

```html
<nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
  <div class="container">
    <a class="navbar-brand fw-bold" href="#">MeuSite</a>
    <button class="navbar-toggler" type="button"
            data-bs-toggle="collapse" data-bs-target="#navMenu"
            aria-controls="navMenu" aria-expanded="false" aria-label="Menu">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navMenu">
      <ul class="navbar-nav ms-auto gap-1">
        <li class="nav-item"><a class="nav-link active" href="#">Início</a></li>
        <li class="nav-item"><a class="nav-link" href="#">Sobre</a></li>
        <li class="nav-item"><a class="nav-link" href="#">Contato</a></li>
      </ul>
      <a href="#" class="btn btn-light btn-sm ms-lg-3">Entrar</a>
    </div>
  </div>
</nav>
```

## Card

```html
<div class="card shadow-sm h-100 border-0">
  <img src="imagem.jpg" class="card-img-top" alt="Descrição da imagem">
  <div class="card-body d-flex flex-column">
    <span class="badge bg-primary mb-2 align-self-start">Categoria</span>
    <h5 class="card-title">Título do Card</h5>
    <p class="card-text text-muted flex-grow-1">Descrição breve do conteúdo do card.</p>
    <a href="#" class="btn btn-primary mt-3">Ver mais</a>
  </div>
  <div class="card-footer text-muted small">Publicado em 23/03/2026</div>
</div>
```

## Modal

```html
<!-- Botão que abre o modal -->
<button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalConfirmar">
  Confirmar
</button>

<!-- Modal -->
<div class="modal fade" id="modalConfirmar" tabindex="-1" aria-labelledby="modalConfirmarLabel" aria-modal="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modalConfirmarLabel">Confirmar ação</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
      </div>
      <div class="modal-body">
        Você tem certeza que deseja realizar esta ação?
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <button type="button" class="btn btn-danger" id="btn-confirmar">Confirmar</button>
      </div>
    </div>
  </div>
</div>
```

## Alerts de Feedback

```html
<!-- Sucesso -->
<div class="alert alert-success alert-dismissible fade show d-none" role="alert" id="feedback">
  <strong>Sucesso!</strong> Operação realizada com êxito.
  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
</div>

<!-- Erro -->
<div class="alert alert-danger" role="alert">
  <strong>Erro!</strong> Não foi possível completar a operação.
</div>
```

## Spinner de Carregamento

```html
<div id="spinner" class="d-none text-center py-4">
  <div class="spinner-border text-primary" role="status">
    <span class="visually-hidden">Carregando...</span>
  </div>
</div>
```

## Classes Utilitárias — Referência Rápida

```
ESPAÇAMENTO
  m-{0-5}     → margin em todos os lados
  p-{0-5}     → padding em todos os lados
  mt-* mb-* ms-* me-* mx-* my-*  → direções específicas
  gap-{0-5}   → gap em flex/grid

DISPLAY
  d-none      → display: none
  d-block     → display: block
  d-flex      → display: flex
  d-grid      → display: grid
  d-{sm|md|lg|xl}-block  → responsivo

FLEXBOX
  justify-content-{start|center|end|between|around}
  align-items-{start|center|end|stretch}
  flex-column     → direção vertical
  flex-wrap       → quebra de linha
  flex-grow-1     → ocupa espaço disponível

TEXTO
  text-{start|center|end}    → alinhamento
  text-muted                 → cinza
  fw-bold fw-normal fw-light → peso
  fs-{1-6}                   → tamanho (1=maior, 6=menor)
  text-truncate              → reticências com overflow

CORES
  text-primary bg-primary
  text-secondary bg-secondary
  text-success bg-success
  text-danger bg-danger
  text-warning bg-warning
  text-white bg-dark bg-light

BORDAS E SOMBRAS
  border border-primary border-0
  rounded rounded-pill rounded-0
  shadow shadow-sm shadow-lg

TAMANHO
  w-{25|50|75|100}   → largura relativa
  h-100 vh-100        → altura total
  mw-100 mh-100       → max-width/height
```