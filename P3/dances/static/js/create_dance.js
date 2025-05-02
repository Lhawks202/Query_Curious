document.addEventListener('DOMContentLoaded', () => {
    const stepsContainer = document.getElementById('stepsContainer');
    const addStepBtn = document.getElementById('addStepBtn');
    let stepCount = 0;

    // TODO: replace this static list with a call to your backend later
    const figures = ['Figure 1', 'Figure 2', 'Figure 3', 'Figure 4'];

    function createStep() {
        const idx = stepCount++;
        const label = String.fromCharCode(65 + idx);       // A, B, C, …
        const collapseId = `collapse${idx}`;

        // outer card
        const card = document.createElement('div');
        card.className = 'card step-card mb-3';

        // header
        const hdr = document.createElement('div');
        hdr.className = 'step-card-header d-flex justify-content-between align-items-center';
        hdr.setAttribute('data-bs-toggle', 'collapse');
        hdr.setAttribute('data-bs-target', `#${collapseId}`);
        hdr.setAttribute('aria-expanded', 'false');
        hdr.setAttribute('aria-controls', collapseId);
        hdr.innerHTML = `<span>${label}</span><i class="bi bi-chevron-down"></i>`;
        card.appendChild(hdr);

        // collapse container
        const coll = document.createElement('div');
        coll.className = 'collapse';
        coll.id = collapseId;

        // body (figure cards go here)
        const body = document.createElement('div');
        body.className = 'card-body bg-dark';
        figures.forEach(name => {
            const fc = document.createElement('div');
            fc.className = 'card figure-card p-2';
            fc.textContent = name;
            body.appendChild(fc);
        });
        coll.appendChild(body);
        card.appendChild(coll);

        stepsContainer.appendChild(card);
    }

    addStepBtn.addEventListener('click', createStep);
});