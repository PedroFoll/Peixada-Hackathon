# Referência HTML — Exemplos e Templates

## Estrutura base de uma página

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Descrição da página para SEO">
  <title>Título da Página</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="./css/styles.css">
</head>
<body>
  <header>
    <nav>...</nav>
  </header>

  <main>
    <section>...</section>
  </main>

  <footer>...</footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js" defer></script>
  <script src="./js/main.js" defer></script>
</body>
</html>
```

## Formulário acessível

```html
<form id="formulario-contato" novalidate>
  <div class="mb-3">
    <label for="nome" class="form-label">Nome completo</label>
    <input type="text" class="form-control" id="nome" name="nome"
           required minlength="3" autocomplete="name"
           aria-describedby="nome-ajuda">
    <div id="nome-ajuda" class="form-text">Digite seu nome completo.</div>
    <div class="invalid-feedback">Por favor, informe seu nome.</div>
  </div>

  <div class="mb-3">
    <label for="email" class="form-label">E-mail</label>
    <input type="email" class="form-control" id="email" name="email"
           required autocomplete="email">
    <div class="invalid-feedback">Informe um e-mail válido.</div>
  </div>

  <div class="mb-3">
    <label for="mensagem" class="form-label">Mensagem</label>
    <textarea class="form-control" id="mensagem" name="mensagem"
              rows="4" required></textarea>
    <div class="invalid-feedback">A mensagem não pode estar vazia.</div>
  </div>

  <button type="submit" class="btn btn-primary">Enviar</button>
</form>
```

## Tabela acessível

```html
<div class="table-responsive">
  <table class="table table-striped table-hover" aria-label="Lista de produtos">
    <thead class="table-dark">
      <tr>
        <th scope="col">#</th>
        <th scope="col">Produto</th>
        <th scope="col">Preço</th>
        <th scope="col">Ações</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th scope="row">1</th>
        <td>Produto A</td>
        <td>R$ 49,90</td>
        <td>
          <button class="btn btn-sm btn-outline-primary" aria-label="Editar Produto A">Editar</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

## Imagens responsivas

```html
<!-- Imagem simples -->
<img src="./assets/images/foto.jpg" alt="Descrição detalhada da imagem"
     width="800" height="450" loading="lazy" class="img-fluid">

<!-- Picture com formatos modernos -->
<picture>
  <source srcset="./assets/images/foto.webp" type="image/webp">
  <source srcset="./assets/images/foto.jpg" type="image/jpeg">
  <img src="./assets/images/foto.jpg" alt="Descrição da imagem"
       width="800" height="450" loading="lazy" class="img-fluid">
</picture>
```

## Ícones acessíveis

```html
<!-- Ícone decorativo (oculto do leitor de tela) -->
<svg aria-hidden="true" focusable="false">...</svg>

<!-- Ícone funcional (com label) -->
<button aria-label="Fechar menu">
  <svg aria-hidden="true" focusable="false">...</svg>
</button>

<!-- Com Bootstrap Icons -->
<i class="bi bi-house" aria-hidden="true"></i> Início
```