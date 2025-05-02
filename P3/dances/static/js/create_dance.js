document.addEventListener('DOMContentLoaded', () => {
    const stepsContainer = document.getElementById('stepsContainer');
    const addStepBtn = document.getElementById('addStepBtn');
    const deleteBtn = document.getElementById('deleteModeBtn');
    const figureModalEl = document.getElementById('figureModal');
    const figureNameInput = document.getElementById('figureNameInput');
    const figureModalSubmit = document.getElementById('figureModalSubmit');
    const figureModal = new bootstrap.Modal(figureModalEl);

    let stepCount = 0;
    let deleteMode = false;
    let pendingAddFn = null;    // will hold the current addFigure callback

    const figures = ['Figure 1', 'Figure 2', 'Figure 3', 'Figure 4'];

    function updateDeleteModeUI() {
        document
            .querySelectorAll('.step-card')
            .forEach(card => card.classList.toggle('shake', deleteMode));
        deleteBtn.classList.toggle('text-danger', !deleteMode);
        deleteBtn.classList.toggle('text-white', deleteMode);
    }

    // Toggle delete mode
    deleteBtn.addEventListener('click', e => {
        e.stopPropagation();
        deleteMode = !deleteMode;
        updateDeleteModeUI();
    });

    // Click outside to exit delete mode
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

    // Delete on card click when in delete mode
    stepsContainer.addEventListener('click', e => {
        if (!deleteMode) return;
        const card = e.target.closest('.step-card');
        if (card) card.remove();
    });

    // Modal submit handler: call the pending addFigure, then clear
    figureModalSubmit.addEventListener('click', () => {
        const name = figureNameInput.value.trim() || 'New Figure';
        if (pendingAddFn) pendingAddFn(name);
        figureNameInput.value = '';
        pendingAddFn = null;
        figureModal.hide();
    });

    function createStep() {
        const idx = stepCount++;
        const label = String.fromCharCode(65 + idx);
        const collapseId = `collapse${idx}`;

        // Outer card
        const card = document.createElement('div');
        card.className = 'shadow-sm step-card mb-3';

        // Header
        const hdr = document.createElement('div');
        hdr.className = 'step-card-header d-flex justify-content-between align-items-center';

        // Label input
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'step-label-input ps-3';
        input.value = label;
        input.placeholder = label;
        input.addEventListener('mousedown', e => e.stopPropagation());
        input.addEventListener('click', e => e.stopPropagation());

        // Chevron
        const icon = document.createElement('i');
        icon.className = 'bi bi-chevron-down pe-3';

        hdr.appendChild(input);
        hdr.appendChild(icon);
        card.appendChild(hdr);

        // Collapse panel
        const coll = document.createElement('div');
        coll.className = 'collapse';
        coll.id = collapseId;

        // Body
        const body = document.createElement('div');
        body.className = 'card-body p-3 d-flex flex-column figure-dropdown';

        // 1) Create & append the "+ Figure" button
        const addFigBtn = document.createElement('button');
        addFigBtn.type = 'button';
        addFigBtn.className = 'btn shadow-sm figure-card p-3 mx-5 add-btn add-btn-figure d-flex justify-content-center align-items-center';
        addFigBtn.innerHTML = '<i class="bi bi-plus"></i>';
        addFigBtn.addEventListener('mousedown', e => e.stopPropagation());
        addFigBtn.addEventListener('click', e => {
            e.stopPropagation();
            // stash the callback and show the modal
            pendingAddFn = addFigure;
            figureModal.show();
        });
        body.appendChild(addFigBtn);

        // 2) Helper that inserts a figure card before that button
        function addFigure(name) {
            const fc = document.createElement('div');
            fc.className = 'shadow-sm figure-card p-3 mx-5';
            fc.textContent = name;
            body.insertBefore(fc, addFigBtn);
        }

        // 3) Seed initial figures
        // figures.forEach(name => addFigure(name));

        // Assemble
        coll.appendChild(body);
        card.appendChild(coll);
        stepsContainer.appendChild(card);

        // Manual collapse toggle
        hdr.addEventListener('click', e => {
            if (e.target === input) return;
            const bsColl = bootstrap.Collapse.getOrCreateInstance(coll);
            bsColl.toggle();
        });

        if (deleteMode) card.classList.add('shake');
    }

    // Wire up the main "Add Step" button
    addStepBtn.addEventListener('click', createStep);
});
