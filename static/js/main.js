// Configurações globais Chart.js
document.addEventListener('DOMContentLoaded', () => {
  if (typeof Chart !== 'undefined') {
    Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.plugins.tooltip.callbacks.label = function (ctx) {
      const val = ctx.parsed.y ?? ctx.parsed;
      if (typeof val === 'number') {
        return ' R$ ' + val.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
      }
      return ctx.label;
    };
  }
});

/**
 * Máscara monetária brasileira (R$ 1.234,56).
 * Aplica em um campo de texto visível e sincroniza o valor decimal
 * em um campo hidden associado (name real enviado ao servidor).
 *
 * @param {HTMLInputElement} displayInput - campo visível (type="text")
 * @param {HTMLInputElement} hiddenInput  - campo hidden (name="valor")
 */
function aplicarMascaraMonetaria(displayInput, hiddenInput) {
  if (!displayInput || !hiddenInput) return;

  function formatarValor(centavos) {
    const valor = (centavos / 100).toFixed(2);
    const [inteiro, decimal] = valor.split('.');
    const inteiroFmt = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return inteiroFmt + ',' + decimal;
  }

  function atualizarCampos(centavos) {
    if (centavos === 0) {
      displayInput.value = '';
      hiddenInput.value = '';
    } else {
      displayInput.value = formatarValor(centavos);
      hiddenInput.value = (centavos / 100).toFixed(2);
    }
  }

  displayInput.addEventListener('input', () => {
    const apenasDigitos = displayInput.value.replace(/\D/g, '');
    const centavos = parseInt(apenasDigitos, 10) || 0;
    atualizarCampos(centavos);
  });

  displayInput.addEventListener('keydown', (e) => {
    const permitidos = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End'];
    if (permitidos.includes(e.key) || e.ctrlKey || e.metaKey) return;
    if (!/^\d$/.test(e.key)) e.preventDefault();
  });
}

/**
 * Define o valor inicial da máscara monetária a partir de um valor decimal.
 * @param {HTMLInputElement} displayInput
 * @param {HTMLInputElement} hiddenInput
 * @param {string|number} valorDecimal - ex: "1234.56" ou 1234.56
 */
function setValorMascaraMonetaria(displayInput, hiddenInput, valorDecimal) {
  if (!displayInput || !hiddenInput) return;
  const num = parseFloat(valorDecimal);
  if (isNaN(num) || num <= 0) {
    displayInput.value = '';
    hiddenInput.value = '';
    return;
  }
  const centavos = Math.round(num * 100);
  const valor = (centavos / 100).toFixed(2);
  const [inteiro, decimal] = valor.split('.');
  const inteiroFmt = inteiro.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  displayInput.value = inteiroFmt + ',' + decimal;
  hiddenInput.value = valor;
}

