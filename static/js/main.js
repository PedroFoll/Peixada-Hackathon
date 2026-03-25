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

