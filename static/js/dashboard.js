document.addEventListener('DOMContentLoaded', () => {
  const CORES_RECEITA = ['#198754', '#20c997', '#0dcaf0', '#0d6efd', '#6f42c1', '#d63384'];
  const CORES_DESPESA = ['#dc3545', '#fd7e14', '#ffc107', '#e83e8c', '#6c757d', '#343a40'];

  const fmtBRL = (val) =>
    'R$ ' + Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2 });

  // === Gráfico Receitas × Despesas (Grouped Bar) ===
  const canvasComparacao = document.getElementById('graficoComparacao');
  if (canvasComparacao) {
    const dados = JSON.parse(canvasComparacao.dataset.comparacao);

    new Chart(canvasComparacao.getContext('2d'), {
      type: 'bar',
      data: {
        labels: dados.labels.length ? dados.labels : ['Sem dados'],
        datasets: [
          {
            label: 'Receitas',
            data: dados.receitas,
            backgroundColor: 'rgba(25, 135, 84, 0.8)',
            borderColor: '#198754',
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: 'Despesas',
            data: dados.despesas,
            backgroundColor: 'rgba(220, 53, 69, 0.8)',
            borderColor: '#dc3545',
            borderWidth: 1,
            borderRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.dataset.label}: ${fmtBRL(ctx.parsed.y)}`,
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (val) => 'R$ ' + Number(val).toLocaleString('pt-BR'),
            },
            grid: { color: 'rgba(0,0,0,.06)' },
          },
          x: { grid: { display: false } },
        },
      },
    });
  }

  // === Função auxiliar para gráfico Donut ===
  function criarDonut(canvasId, coresBase) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const dados = JSON.parse(canvas.dataset.dados);
    const semDados = !dados.labels || dados.labels.length === 0;

    new Chart(canvas.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: semDados ? ['Sem dados'] : dados.labels,
        datasets: [
          {
            data: semDados ? [1] : dados.valores,
            backgroundColor: semDados
              ? ['#dee2e6']
              : dados.cores.length
              ? dados.cores
              : coresBase.slice(0, dados.labels.length),
            borderWidth: 2,
            borderColor: '#ffffff',
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'right',
            labels: { padding: 12, usePointStyle: true, pointStyleWidth: 10 },
          },
          tooltip: {
            callbacks: {
              label: (ctx) =>
                semDados
                  ? ' Sem lançamentos'
                  : ` ${ctx.label}: ${fmtBRL(ctx.parsed)}`,
            },
          },
        },
      },
    });
  }

  criarDonut('graficoReceitasCat', CORES_RECEITA);
  criarDonut('graficoDespesasCat', CORES_DESPESA);

  // === Modais de movimentação ===
  function configurarModalMovimentacao(prefixo, modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    const inputData        = document.getElementById(`${prefixo}-data`);
    const checkRecorrente  = document.getElementById(`${prefixo}-recorrente`);
    const camposRec        = document.getElementById(`${prefixo}-campos-recorrencia`);
    const selectFrequencia = document.getElementById(`${prefixo}-frequencia`);
    const camposSemanal    = document.getElementById(`${prefixo}-campos-semanal`);
    const camposMensal     = document.getElementById(`${prefixo}-campos-mensal`);

    modal.addEventListener('show.bs.modal', () => {
      if (inputData && !inputData.value) {
        inputData.value = new Date().toISOString().split('T')[0];
      }
    });

    if (!checkRecorrente) return;

    checkRecorrente.addEventListener('change', () => {
      const ativo = checkRecorrente.checked;
      camposRec.style.display = ativo ? 'block' : 'none';
      if (!ativo) {
        selectFrequencia.value = '';
        camposSemanal.style.display = 'none';
        camposMensal.style.display = 'none';
      }
    });

    selectFrequencia.addEventListener('change', () => {
      camposSemanal.style.display = selectFrequencia.value === 'semanal' ? 'block' : 'none';
      camposMensal.style.display  = selectFrequencia.value === 'mensal'  ? 'block' : 'none';
    });
  }

  configurarModalMovimentacao('r', 'modalNovaReceita');
  configurarModalMovimentacao('d', 'modalNovaDespesa');

  // === Preview de ícone no modal de categoria ===
  const selectIcone = document.getElementById('cat-icone');
  const previewIcone = document.querySelector('#cat-icone-preview i');
  if (selectIcone && previewIcone) {
    selectIcone.addEventListener('change', () => {
      previewIcone.className = `bi ${selectIcone.value}`;
    });
  }
});
