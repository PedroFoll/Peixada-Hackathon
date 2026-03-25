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
    const spanNome    = document.getElementById('excluir-cat-nome');
    const avisoDiv    = document.getElementById('excluir-cat-aviso');
    const spanCount   = document.getElementById('excluir-cat-count');
    const spanPlural  = document.getElementById('excluir-cat-plural');
    const spanPlural2 = document.getElementById('excluir-cat-plural2');

    modalExcluir.addEventListener('show.bs.modal', (event) => {
      const btn   = event.relatedTarget;
      const pk    = btn.dataset.pk;
      const nome  = btn.dataset.nome;
      const count = parseInt(btn.dataset.count, 10);

      formExcluir.action = actionBase.replace('/0/', `/${pk}/`);
      spanNome.textContent = nome;

      if (count > 0) {
        spanCount.textContent  = count;
        spanPlural.textContent = count === 1 ? 'ão' : 'ões';
        spanPlural2.textContent = count === 1 ? '' : 's';
        avisoDiv.classList.remove('d-none');
      } else {
        avisoDiv.classList.add('d-none');
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
