# Referência JavaScript — Exemplos e Templates

## Manipulação do DOM

```js
// === SELEÇÃO ===
const btn        = document.querySelector('#meu-botao');
const cards      = document.querySelectorAll('.card');
const formulario = document.querySelector('form');

// === CRIAR E INSERIR ELEMENTO ===
function criarElemento(tag, classes = [], texto = '') {
  const el = document.createElement(tag);
  if (classes.length) el.classList.add(...classes);
  if (texto) el.textContent = texto; // textContent é seguro (evita XSS)
  return el;
}

// Inserir no DOM
const container = document.querySelector('#container');
container.appendChild(criarElemento('p', ['texto-destaque'], 'Olá mundo'));

// === TOGGLE DE CLASSE ===
btn.addEventListener('click', () => {
  document.querySelector('.menu').classList.toggle('ativo');
});

// === DELEGAÇÃO DE EVENTOS (para listas dinâmicas) ===
document.querySelector('#lista').addEventListener('click', (e) => {
  if (e.target.matches('.btn-remover')) {
    e.target.closest('li').remove();
  }
});
```

## Consumo de API REST

```js
// === FETCH COM TRATAMENTO DE ERROS ===
async function buscarDados(url) {
  try {
    const resposta = await fetch(url);
    if (!resposta.ok) throw new Error(`Erro HTTP ${resposta.status}: ${resposta.statusText}`);
    return await resposta.json();
  } catch (erro) {
    console.error('Falha ao buscar dados:', erro.message);
    throw erro;
  }
}

// === POST COM JSON ===
async function enviarDados(url, dados) {
  try {
    const resposta = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados),
    });
    if (!resposta.ok) throw new Error(`Erro HTTP ${resposta.status}`);
    return await resposta.json();
  } catch (erro) {
    console.error('Falha ao enviar dados:', erro.message);
    throw erro;
  }
}

// === USO ===
async function carregarProdutos() {
  mostrarCarregando(true);
  try {
    const produtos = await buscarDados('/api/produtos');
    renderizarProdutos(produtos);
  } catch {
    mostrarErro('Não foi possível carregar os produtos.');
  } finally {
    mostrarCarregando(false);
  }
}
```

## Validação de Formulário

```js
// === VALIDAÇÃO MANUAL ===
function validarFormulario(form) {
  const campos = form.querySelectorAll('[required]');
  let valido = true;

  campos.forEach(campo => {
    const erro = campo.closest('.mb-3')?.querySelector('.invalid-feedback');
    if (!campo.value.trim()) {
      campo.classList.add('is-invalid');
      campo.classList.remove('is-valid');
      valido = false;
    } else {
      campo.classList.remove('is-invalid');
      campo.classList.add('is-valid');
    }
  });

  return valido;
}

// === EVENTO DE SUBMIT ===
document.querySelector('#formulario').addEventListener('submit', async (e) => {
  e.preventDefault();
  if (!validarFormulario(e.target)) return;

  const dados = Object.fromEntries(new FormData(e.target));
  try {
    await enviarDados('/api/contato', dados);
    mostrarSucesso('Mensagem enviada com sucesso!');
    e.target.reset();
  } catch {
    mostrarErro('Erro ao enviar. Tente novamente.');
  }
});
```

## Gráficos com Chart.js

CDN: `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`

```js
// === GRÁFICO DE BARRAS ===
function criarGraficoBarras(canvasId, labels, dados, titulo) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: titulo,
        data: dados,
        backgroundColor: 'rgba(59, 130, 246, 0.7)',
        borderColor: '#3b82f6',
        borderWidth: 2,
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        title: { display: !!titulo, text: titulo }
      },
      scales: { y: { beginAtZero: true } }
    }
  });
}

// === GRÁFICO DE LINHA ===
function criarGraficoLinha(canvasId, labels, datasets) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      tension: 0.4, // curva suave
      plugins: { legend: { position: 'top' } }
    }
  });
}

// === GRÁFICO DE PIZZA / ROSCA ===
function criarGraficoPizza(canvasId, labels, dados, tipo = 'pie') {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: tipo, // 'pie' ou 'doughnut'
    data: {
      labels,
      datasets: [{
        data: dados,
        backgroundColor: ['#3b82f6','#f59e0b','#22c55e','#ef4444','#8b5cf6'],
      }]
    },
    options: { responsive: true, plugins: { legend: { position: 'right' } } }
  });
}

// === USO ===
criarGraficoBarras('grafico-vendas',
  ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
  [120, 190, 300, 250, 420, 380],
  'Vendas Mensais'
);
```

## Funções Utilitárias

```js
// === utils.js ===

/** Debounce — evita chamadas excessivas (ex: campo de busca) */
export function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/** Formata número como moeda brasileira */
export const formatarBRL = valor =>
  valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

/** Formata data para pt-BR */
export const formatarData = (data, opcoes = {}) =>
  new Date(data).toLocaleDateString('pt-BR', {
    day: '2-digit', month: 'long', year: 'numeric', ...opcoes
  });

/** Mostra/esconde spinner de carregamento */
export function mostrarCarregando(ativo, seletor = '#spinner') {
  const spinner = document.querySelector(seletor);
  if (spinner) spinner.classList.toggle('d-none', !ativo);
}

/** Exibe mensagem de feedback */
export function mostrarFeedback(mensagem, tipo = 'success', seletor = '#feedback') {
  const el = document.querySelector(seletor);
  if (!el) return;
  el.textContent = mensagem;
  el.className = `alert alert-${tipo}`;
  el.classList.remove('d-none');
  setTimeout(() => el.classList.add('d-none'), 4000);
}

/** Trunca texto longo */
export const truncar = (texto, limite = 100) =>
  texto.length > limite ? texto.slice(0, limite).trimEnd() + '…' : texto;
```