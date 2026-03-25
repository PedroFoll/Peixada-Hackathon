document.addEventListener('DOMContentLoaded', () => {
  const fmtBRL = (val) =>
    'R$ ' + Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  // ── Edit modal ────────────────────────────────────────────────
  const modalEditar = document.getElementById('modalEditarLancamento');
  if (modalEditar) {
    const formEditar = modalEditar.querySelector('#form-editar');

    modalEditar.addEventListener('show.bs.modal', (event) => {
      const btn = event.relatedTarget;
      const pk       = btn.dataset.pk;
      const tipo     = btn.dataset.tipo;
      const valor    = btn.dataset.valor;
      const dataVal  = btn.dataset.data;
      const catId    = btn.dataset.categoriaId || '';
      const descr    = btn.dataset.descricao || '';
      const recor    = btn.dataset.recorrente === 'true';
      const freq     = btn.dataset.frequencia || '';
      const diaMes   = btn.dataset.diaMes || '';
      const dataLim  = btn.dataset.dataLimite || '';
      const diasSem  = btn.dataset.diasSemana || '';

      // Form action
      formEditar.action = formEditar.dataset.actionBase.replace('/0/', `/${pk}/`);

      // Modal title + button color
      const icone  = document.getElementById('e-icone-tipo');
      const titulo = document.getElementById('e-titulo-texto');
      const btnSalvar = document.getElementById('e-btn-salvar');
      if (tipo === 'receita') {
        icone.className  = 'bi bi-arrow-up-circle-fill text-success me-2';
        titulo.textContent = 'Editar Receita';
        btnSalvar.className = 'btn btn-success';
      } else {
        icone.className  = 'bi bi-arrow-down-circle-fill text-danger me-2';
        titulo.textContent = 'Editar Despesa';
        btnSalvar.className = 'btn btn-danger';
      }

      // Basic fields
      document.getElementById('e-tipo').value      = tipo;
      document.getElementById('e-categoria').value = catId;
      document.getElementById('e-valor').value     = valor;
      document.getElementById('e-data').value      = dataVal;
      document.getElementById('e-descricao').value = descr;

      // Recorrência
      const checkRec   = document.getElementById('e-recorrente');
      const camposRec  = document.getElementById('e-campos-recorrencia');
      checkRec.checked = recor;
      camposRec.style.display = recor ? 'block' : 'none';

      const selectFreq    = document.getElementById('e-frequencia');
      const camposSemanal = document.getElementById('e-campos-semanal');
      const camposMensal  = document.getElementById('e-campos-mensal');
      selectFreq.value = freq;
      camposSemanal.style.display = (freq === 'semanal') ? 'block' : 'none';
      camposMensal.style.display  = (freq === 'mensal')  ? 'block' : 'none';

      // Dias da semana
      const diasAtivos = diasSem ? diasSem.split(',').map(d => d.trim()) : [];
      ['0', '1', '2', '3', '4', '5', '6'].forEach(d => {
        const cb = document.getElementById(`e-dia-${d}`);
        if (cb) cb.checked = diasAtivos.includes(d);
      });

      document.getElementById('e-dia-mes').value     = diaMes;
      document.getElementById('e-data-limite').value = dataLim;
    });

    // Recorrência toggle
    const checkRecEdit = document.getElementById('e-recorrente');
    if (checkRecEdit) {
      checkRecEdit.addEventListener('change', (e) => {
        const campos = document.getElementById('e-campos-recorrencia');
        campos.style.display = e.target.checked ? 'block' : 'none';
        if (!e.target.checked) {
          document.getElementById('e-frequencia').value = '';
          document.getElementById('e-campos-semanal').style.display = 'none';
          document.getElementById('e-campos-mensal').style.display  = 'none';
        }
      });
    }

    // Frequência toggle
    const selectFreqEdit = document.getElementById('e-frequencia');
    if (selectFreqEdit) {
      selectFreqEdit.addEventListener('change', (e) => {
        document.getElementById('e-campos-semanal').style.display = (e.target.value === 'semanal') ? 'block' : 'none';
        document.getElementById('e-campos-mensal').style.display  = (e.target.value === 'mensal')  ? 'block' : 'none';
      });
    }
  }

  // ── Delete modal ──────────────────────────────────────────────
  const modalExcluir = document.getElementById('modalExcluirLancamento');
  if (modalExcluir) {
    const formExcluir = modalExcluir.querySelector('#form-excluir');

    modalExcluir.addEventListener('show.bs.modal', (event) => {
      const btn   = event.relatedTarget;
      const pk    = btn.dataset.pk;
      const descr = btn.dataset.descricao || '—';
      const valor = btn.dataset.valor;
      const tipo  = btn.dataset.tipo;

      formExcluir.action = formExcluir.dataset.actionBase.replace('/0/', `/${pk}/`);

      document.getElementById('excluir-descricao').textContent = descr;
      document.getElementById('excluir-valor').textContent     = fmtBRL(valor);
      document.getElementById('excluir-tipo').textContent      = tipo === 'receita' ? 'Receita' : 'Despesa';
    });
  }

  // ── Auto-fill today's date on create modals ───────────────────
  const today = new Date().toISOString().split('T')[0];
  [['modalNovaReceita', 'r-data'], ['modalNovaDespesa', 'd-data']].forEach(([modalId, inputId]) => {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.addEventListener('show.bs.modal', () => {
      const input = document.getElementById(inputId);
      if (input && !input.value) input.value = today;
    });
  });

  // ── Recorrência toggle for Nova Receita ───────────────────────
  configurarRecorrenciaModal('r');

  // ── Recorrência toggle for Nova Despesa ───────────────────────
  configurarRecorrenciaModal('d');

  function configurarRecorrenciaModal(p) {
    const checkRec = document.getElementById(`${p}-recorrente`);
    if (!checkRec) return;

    checkRec.addEventListener('change', (e) => {
      const campos = document.getElementById(`${p}-campos-recorrencia`);
      if (campos) {
        campos.style.display = e.target.checked ? 'block' : 'none';
        if (!e.target.checked) {
          const freq = document.getElementById(`${p}-frequencia`);
          if (freq) freq.value = '';
          const sem = document.getElementById(`${p}-campos-semanal`);
          if (sem) sem.style.display = 'none';
          const men = document.getElementById(`${p}-campos-mensal`);
          if (men) men.style.display = 'none';
        }
      }
    });

    const selectFreq = document.getElementById(`${p}-frequencia`);
    if (selectFreq) {
      selectFreq.addEventListener('change', (e) => {
        const sem = document.getElementById(`${p}-campos-semanal`);
        const men = document.getElementById(`${p}-campos-mensal`);
        if (sem) sem.style.display = (e.target.value === 'semanal') ? 'block' : 'none';
        if (men) men.style.display = (e.target.value === 'mensal')  ? 'block' : 'none';
      });
    }
  }
});
