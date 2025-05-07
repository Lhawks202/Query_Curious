document.addEventListener('DOMContentLoaded', () => {
  const stepsContainer = document.getElementById('stepsContainer');
  const addStepBtn = document.getElementById('addStepBtn');
  const deleteBtn = document.getElementById('deleteModeBtn');

  const figureModalEl = document.getElementById('figureModal');

  const figureModal = new bootstrap.Modal(figureModalEl);

  let pendingAddFn = null;

  let stepCount = 0;
  let deleteMode = false;

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
      !e.target.closest('.step-card') &&
      !e.target.closest('.figure-card')
    ) {
      deleteMode = false;
      updateDeleteModeUI();
    }
  });

  stepsContainer.addEventListener('click', e => {
    if (!deleteMode) return;
    const fig = e.target.closest('.figure-card');
    if (fig) {
      fig.remove();
    }
    const step = e.target.closest('.step-card');
    if (step) step.remove();
  });

  function createStep() {
    const idx = stepCount++;
    const collapseId = `collapse${idx}`;

    const card = document.createElement('div');
    card.className = 'shadow-sm step-card mb-4';

    const hdr = document.createElement('div');
    hdr.className = 'step-card-header d-flex justify-content-between align-items-center';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'step-label-input ms-2 ps-1';
    input.placeholder = "Enter Step Name";
    input.addEventListener('mousedown', e => e.stopPropagation());
    input.addEventListener('click', e => e.stopPropagation());

    const icon = document.createElement('i');
    icon.className = 'bi bi-chevron-down pe-3';

    hdr.appendChild(input);
    hdr.appendChild(icon);
    card.appendChild(hdr);

    const coll = document.createElement('div');
    coll.className = 'collapse';
    coll.id = collapseId;

    const body = document.createElement('div');
    body.className = 'card-body p-3 d-flex flex-column figure-dropdown';

    const addFigBtn = document.createElement('button');
    addFigBtn.type = 'button';
    addFigBtn.className = 'btn shadow-sm figure-card p-3 mx-5 add-btn add-btn-figure d-flex justify-content-center align-items-center';
    addFigBtn.setAttribute('data-bs-toggle', 'tooltip');
    addFigBtn.setAttribute('data-bs-placement', 'top');
    addFigBtn.setAttribute('title', 'Click to add a new figure');
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

  const figureForm = document.getElementById('figureForm');
  const nameInput = document.getElementById('figureNameInput');
  const rolesInput = document.getElementById('rolesInput');
  const startPosInput = document.getElementById('startPosInput');
  const actionInput = document.getElementById('actionInput');
  const endPosInput = document.getElementById('endPosInput');
  const durationInput = document.getElementById('durationInput');

  figureForm.addEventListener('submit', e => {
    e.preventDefault();

    const payload = {
      name: nameInput.value.trim(),
      roles: rolesInput.value.trim(),
      start_position: startPosInput.value.trim(),
      action: actionInput.value.trim(),
      end_position: endPosInput.value.trim(),
      duration: parseInt(durationInput.value, 10)
    };

    if (Object.values(payload).some(v => v === '' || v == null || isNaN(payload.duration))) {
      return alert('Please fill out all fields');
    }

    fetch(`${figureForm.getAttribute('action')}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(res => {
        if (!res.ok) throw new Error('Save failed');
        return res.json();
      })
      .then(data => {
        pendingAddFn(data.name);
        figureForm.reset();
        figureModal.hide();
      })
      .catch(err => {
        console.error(err);
        alert('Could not save figure. Try again.');
      });
  });

  const searchForm = document.getElementById('figureSearchForm');
  const searchInput = document.getElementById('figureSearchInput');
  const resultsHolder = document.getElementById('figureSearchResults');

  searchForm.addEventListener('submit', e => {
    e.preventDefault();
    const q = searchInput.value.trim();
    if (!q) return;

    resultsHolder.innerHTML = '<p>Searching…</p>';

    fetch(searchForm.getAttribute('action'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ q })
    })
      .then(r => r.json())
      .then(list => {
        if (list.length === 0) {
          resultsHolder.innerHTML = '<p>No matches found.</p>';
          return;
        }
        resultsHolder.innerHTML = '';
        list.forEach(fig => {
          const card = document.createElement('div');
          card.className = 'card mb-2';
          card.innerHTML = `
            <div class="card-body">
              <h5 class="card-title">${fig.name}</h5>
              <p class="card-text"><strong>Roles:</strong> ${fig.roles}</p>
              <p class="card-text"><strong>Action:</strong> ${fig.action}</p>
              <!-- … add other fields as you like … -->
            </div>
          `;
          card.addEventListener('click', () => {
            pendingAddFn(fig.name);
            figureModal.hide();
          });
          resultsHolder.appendChild(card);
        });
      })
      .catch(err => {
        console.error(err);
        resultsHolder.innerHTML = '<p class="text-danger">Search failed.</p>';
      });
  });

  const danceForm = document.getElementById('danceForm');
  const danceData = document.getElementById('danceData');
  const danceNameInput = document.querySelector('.danceNameInput');
  const videoInput = document.querySelector('.videoInput');
  const sourceInput = document.querySelector('.sourceInput');

  danceForm.addEventListener('submit', e => {
    const steps = Array.from(document.querySelectorAll('.step-card')).map(card => {
      const stepName = card.querySelector('.step-label-input').value;
      const figures = Array.from(card.querySelectorAll('.figure-card')).map(figureCard => figureCard.textContent.trim()).filter(name => name.length > 0);
      return { stepName, figures }
    });

    const payload = {
      danceName: danceNameInput.value.trim() || 'Untitled Dance',
      video: videoInput.value.trim(),
      source: sourceInput.value.trim(),
      steps
    };

    danceData.value = JSON.stringify(payload);
  });
});
