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

  // === Modal Novo Lançamento (unificado) ===
  const modalNovo = document.getElementById('modalNovoLancamento');
  if (modalNovo) {
    function aplicarTipoNovo(tipo) {
      const icone     = document.getElementById('n-icone-tipo');
      const titulo    = document.getElementById('n-titulo-texto');
      const btnSalvar = document.getElementById('n-btn-salvar');
      const btnTexto  = document.getElementById('n-btn-texto');
      document.getElementById('n-tipo').value = tipo;
      if (tipo === 'receita') {
        icone.className    = 'bi bi-arrow-up-circle-fill text-success me-2';
        titulo.textContent = 'Nova Receita';
        btnSalvar.className = 'btn btn-success';
        btnTexto.textContent = 'Salvar Receita';
        document.getElementById('n-toggle-receita').checked = true;
      } else {
        icone.className    = 'bi bi-arrow-down-circle-fill text-danger me-2';
        titulo.textContent = 'Nova Despesa';
        btnSalvar.className = 'btn btn-danger';
        btnTexto.textContent = 'Salvar Despesa';
        document.getElementById('n-toggle-despesa').checked = true;
      }
    }

    modalNovo.addEventListener('show.bs.modal', (event) => {
      const tipo = event.relatedTarget?.dataset?.tipo || 'receita';
      aplicarTipoNovo(tipo);
      const inputData = document.getElementById('n-data');
      if (inputData && !inputData.value) {
        inputData.value = new Date().toISOString().split('T')[0];
      }
    });

    modalNovo.addEventListener('hidden.bs.modal', () => {
      modalNovo.querySelector('form')?.reset();
      document.getElementById('n-campos-recorrencia').style.display = 'none';
      document.getElementById('n-campos-semanal').style.display = 'none';
      document.getElementById('n-campos-mensal').style.display = 'none';
    });

    document.getElementById('n-toggle-receita')?.addEventListener('change', () => aplicarTipoNovo('receita'));
    document.getElementById('n-toggle-despesa')?.addEventListener('change', () => aplicarTipoNovo('despesa'));

    document.getElementById('n-recorrente')?.addEventListener('change', (e) => {
      document.getElementById('n-campos-recorrencia').style.display = e.target.checked ? 'block' : 'none';
      if (!e.target.checked) {
        document.getElementById('n-frequencia').value = '';
        document.getElementById('n-campos-semanal').style.display = 'none';
        document.getElementById('n-campos-mensal').style.display = 'none';
      }
    });

    document.getElementById('n-frequencia')?.addEventListener('change', (e) => {
      document.getElementById('n-campos-semanal').style.display = (e.target.value === 'semanal') ? 'block' : 'none';
      document.getElementById('n-campos-mensal').style.display  = (e.target.value === 'mensal')  ? 'block' : 'none';
    });
  }

  // === Preview de ícone no modal de categoria ===
  const selectIcone = document.getElementById('cat-icone');
  const previewIcone = document.querySelector('#cat-icone-preview i');
  if (selectIcone && previewIcone) {
    selectIcone.addEventListener('change', () => {
      previewIcone.className = `bi ${selectIcone.value}`;
    });
  }

  // === Toggle filtro por data personalizada ===
  const btnPersonalizado  = document.getElementById('btn-filtro-personalizado');
  const formPersonalizado = document.getElementById('form-personalizado');
  if (btnPersonalizado && formPersonalizado) {
    btnPersonalizado.addEventListener('click', () => {
      const estaOculto = formPersonalizado.classList.contains('d-none');
      formPersonalizado.classList.toggle('d-none', !estaOculto);
      btnPersonalizado.classList.toggle('btn-primary', estaOculto);
      btnPersonalizado.classList.toggle('btn-outline-secondary', !estaOculto);
      btnPersonalizado.setAttribute('aria-expanded', String(estaOculto));
      if (estaOculto) {
        document.getElementById('di-data-inicio')?.focus();
      }
    });
  }
});
