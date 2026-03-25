'use strict';

document.addEventListener('DOMContentLoaded', () => {

  // === Modal: Editar Categoria ===
  const modalEditar = document.getElementById('modalEditarCategoria');
  if (modalEditar) {
    const actionBase = modalEditar.dataset.actionBase;
    const formEditar = document.getElementById('form-editar-categoria');
    const inputNome  = document.getElementById('e-cat-nome');
    const inputCor   = document.getElementById('e-cat-cor');
    const selectIcone = document.getElementById('e-cat-icone');
    const previewIcone = document.querySelector('#e-cat-icone-preview i');

    modalEditar.addEventListener('show.bs.modal', (event) => {
      const btn = event.relatedTarget;
      const pk    = btn.dataset.pk;
      const nome  = btn.dataset.nome;
      const cor   = btn.dataset.cor;
      const icone = btn.dataset.icone;

      formEditar.action = actionBase.replace('/0/', `/${pk}/`);
      inputNome.value = nome;
      inputCor.value  = cor;

      // Seleciona a opção correspondente ao ícone atual
      for (const opt of selectIcone.options) {
        opt.selected = (opt.value === icone);
      }
      // Atualiza preview
      if (previewIcone) {
        previewIcone.className = `bi ${icone}`;
      }
    });

    // Preview ao trocar ícone no modal de edição
    if (selectIcone && previewIcone) {
      selectIcone.addEventListener('change', () => {
        previewIcone.className = `bi ${selectIcone.value}`;
      });
    }
  }

  // === Modal: Excluir Categoria ===
  const modalExcluir = document.getElementById('modalExcluirCategoria');
  if (modalExcluir) {
    const actionBase = modalExcluir.dataset.actionBase;
    const formExcluir = document.getElementById('form-excluir-categoria');

    // Elementos do estado «bloqueado»
    const bloqueadoBody   = document.getElementById('excluir-cat-bloqueado');
    const bloqueadoFooter = document.getElementById('excluir-cat-bloqueado-footer');
    const spanNomeBlocked  = document.getElementById('excluir-cat-nome-blocked');
    const spanCountBlocked = document.getElementById('excluir-cat-count-blocked');
    const spanPluralBlocked  = document.getElementById('excluir-cat-plural-blocked');
    const spanPlural2Blocked = document.getElementById('excluir-cat-plural2-blocked');

    // Elementos do estado «permitido»
    const permitidoBody   = document.getElementById('excluir-cat-permitido');
    const permitidoFooter = document.getElementById('excluir-cat-permitido-footer');
    const spanNome = document.getElementById('excluir-cat-nome');

    modalExcluir.addEventListener('show.bs.modal', (event) => {
      const btn   = event.relatedTarget;
      const pk    = btn.dataset.pk;
      const nome  = btn.dataset.nome;
      const count = parseInt(btn.dataset.count, 10);

      if (count > 0) {
        // Bloqueado: mostra aviso, esconde form de exclusão
        spanNomeBlocked.textContent   = nome;
        spanCountBlocked.textContent  = count;
        spanPluralBlocked.textContent  = count === 1 ? 'ão' : 'ões';
        spanPlural2Blocked.textContent = count === 1 ? '' : 's';
        bloqueadoBody.classList.remove('d-none');
        bloqueadoFooter.classList.remove('d-none');
        permitidoBody.classList.add('d-none');
        permitidoFooter.classList.add('d-none');
      } else {
        // Permitido: mostra confirmação normal
        formExcluir.action = actionBase.replace('/0/', `/${pk}/`);
        spanNome.textContent = nome;
        permitidoBody.classList.remove('d-none');
        permitidoFooter.classList.remove('d-none');
        bloqueadoBody.classList.add('d-none');
        bloqueadoFooter.classList.add('d-none');
      }
    });
  }

  // === Preview de ícone no modal Nova Categoria ===
  const selectNovo   = document.getElementById('n-cat-icone');
  const previewNovo  = document.querySelector('#n-cat-icone-preview i');
  if (selectNovo && previewNovo) {
    selectNovo.addEventListener('change', () => {
      previewNovo.className = `bi ${selectNovo.value}`;
    });
  }

  // Reseta o modal Nova Categoria ao fechar
  const modalNova = document.getElementById('modalNovaCategoria');
  if (modalNova) {
    modalNova.addEventListener('hidden.bs.modal', () => {
      const form = modalNova.querySelector('form');
      if (form) form.reset();
      if (previewNovo) previewNovo.className = 'bi bi-tag';
    });
  }

});
