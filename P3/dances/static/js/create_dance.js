document.addEventListener('DOMContentLoaded', () => {
    const stepsContainer     = document.getElementById('stepsContainer');
    const addStepBtn         = document.getElementById('addStepBtn');
    const deleteBtn          = document.getElementById('deleteModeBtn');
  
    // 1) Grab the modal + inputs
    const figureModalEl      = document.getElementById('figureModal');
    // const figureNameInput    = document.getElementById('figureNameInput');
    // const figureNamePreview  = document.getElementById('figureNamePreview');
    // const figureModalSubmit  = document.getElementById('figureModalSubmit');
    // const toConfirmBtn       = document.getElementById('toConfirmBtn');
    // const backBtn            = document.getElementById('backBtn');
    // const slider             = document.getElementById('figureSlider');
  
    // 2) Initialize Bootstrap’s modal
    const figureModal = new bootstrap.Modal(figureModalEl);
  
    // 3) pendingAddFn must be declared before we use it
    let pendingAddFn = null;
  
    let stepCount  = 0;
    let deleteMode = false;
  
    const figures = ['Figure 1', 'Figure 2', 'Figure 3', 'Figure 4'];
  
    function updateDeleteModeUI() {
      document
        .querySelectorAll('.step-card')
        .forEach(card => card.classList.toggle('shake', deleteMode));
      deleteBtn.classList.toggle('text-danger', !deleteMode);
      deleteBtn.classList.toggle('text-white', deleteMode);
    }
  
    deleteBtn.addEventListener('click', e => {
      e.stopPropagation();
      deleteMode = !deleteMode;
      updateDeleteModeUI();
    });
  
    document.addEventListener('click', e => {
      if (
        deleteMode &&
        !e.target.closest('#deleteModeBtn') &&
        !e.target.closest('.step-card')
      ) {
        deleteMode = false;
        updateDeleteModeUI();
      }
    });
  
    stepsContainer.addEventListener('click', e => {
      if (!deleteMode) return;
      const card = e.target.closest('.step-card');
      if (card) card.remove();
    });
  
    function createStep() {
      const idx        = stepCount++;
      const label      = String.fromCharCode(65 + idx);
      const collapseId = `collapse${idx}`;
  
      const card = document.createElement('div');
      card.className = 'shadow-sm step-card mb-3';
  
      const hdr = document.createElement('div');
      hdr.className = 'step-card-header d-flex justify-content-between align-items-center';
  
      const input = document.createElement('input');
      input.type        = 'text';
      input.className   = 'step-label-input ps-3';
      input.value       = label;
      input.placeholder = label;
      input.addEventListener('mousedown', e => e.stopPropagation());
      input.addEventListener('click',      e => e.stopPropagation());
  
      const icon = document.createElement('i');
      icon.className = 'bi bi-chevron-down pe-3';
  
      hdr.appendChild(input);
      hdr.appendChild(icon);
      card.appendChild(hdr);
  
      const coll = document.createElement('div');
      coll.className = 'collapse';
      coll.id        = collapseId;
  
      const body = document.createElement('div');
      body.className = 'card-body p-3 d-flex flex-column figure-dropdown';
  
      // + Figure button
      const addFigBtn = document.createElement('button');
      addFigBtn.type = 'button';
      addFigBtn.className = 'btn shadow-sm figure-card p-3 mx-5 add-btn add-btn-figure d-flex justify-content-center align-items-center';
      addFigBtn.innerHTML = '<i class="bi bi-plus"></i>';
      addFigBtn.addEventListener('mousedown', e => e.stopPropagation());
      addFigBtn.addEventListener('click', e => {
        e.stopPropagation();
        pendingAddFn = addFigure;
        figureModal.show();
      });
      body.appendChild(addFigBtn);
  
      function addFigure(name) {
        const fc = document.createElement('div');
        fc.className = 'shadow-sm figure-card p-3 mx-5';
        fc.textContent = name;
        body.insertBefore(fc, addFigBtn);
      }
  
      coll.appendChild(body);
      card.appendChild(coll);
      stepsContainer.appendChild(card);
  
      hdr.addEventListener('click', e => {
        if (e.target === input) return;
        const bsColl = bootstrap.Collapse.getOrCreateInstance(coll);
        bsColl.toggle();
      });
  
      if (deleteMode) card.classList.add('shake');
    }
  
    addStepBtn.addEventListener('click', createStep);
  });
  