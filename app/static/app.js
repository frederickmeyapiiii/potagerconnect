document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('[data-post-form]');
  const list = document.querySelector('[data-post-list]');
  const photos = document.querySelectorAll('[data-photo]');
  const modal = document.querySelector('[data-modal]');
  const modalImage = modal?.querySelector('.modal-image');
  const modalTitle = modal?.querySelector('.modal-title');
  const modalCaption = modal?.querySelector('.modal-caption');
  const closeButtons = modal?.querySelectorAll('[data-close]');

  // Formulaires de gestion
  const plotForm = document.querySelector('[data-plot-form]');
  const plotList = document.querySelector('[data-plot-list]');
  const taskForm = document.querySelector('[data-task-form]');
  const taskList = document.querySelector('[data-task-list]');
  const harvestForm = document.querySelector('[data-harvest-form]');
  const harvestList = document.querySelector('[data-harvest-list]');

  photos.forEach((photoCard) => {
    photoCard.addEventListener('click', () => {
      const image = photoCard.dataset.photo;
      const title = photoCard.dataset.title;
      const caption = photoCard.dataset.caption;
      if (!modal || !modalImage || !modalTitle || !modalCaption) return;
      modalImage.src = image;
      modalImage.alt = title;
      modalTitle.textContent = title;
      modalCaption.textContent = caption;
      modal.classList.remove('hidden');
    });
  });

  closeButtons?.forEach((button) => {
    button.addEventListener('click', () => {
      modal?.classList.add('hidden');
    });
  });

  form?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const author = form.querySelector('[name="author"]').value.trim();
    const message = form.querySelector('[name="message"]').value.trim();
    const kind = form.querySelector('[name="kind"]').value;

    if (!message) return;

    const response = await fetch('/api/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author, message, kind })
    });

    if (response.ok) {
      const post = await response.json();
      const item = document.createElement('article');
      item.className = 'post-card';
      item.innerHTML = `
        <div class="post-meta">
          <div class="post-author">
            <span class="author-avatar">${(post.author || 'A')[0].toUpperCase()}</span>
            <strong>${post.author || 'Anonyme'}</strong>
          </div>
          <span class="post-kind post-kind-${post.kind.toLowerCase()}">${post.kind}</span>
        </div>
        <p>${post.message}</p>
      `;
      list.prepend(item);
      form.reset();
    }
  });

  // Gestion des parcelles
  plotForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {
      name: plotForm.querySelector('[name="name"]').value.trim(),
      gardener: plotForm.querySelector('[name="gardener"]').value.trim(),
      crop: plotForm.querySelector('[name="crop"]').value.trim(),
      status: plotForm.querySelector('[name="status"]').value,
      season: plotForm.querySelector('[name="season"]').value,
      rotation: plotForm.querySelector('[name="rotation"]').value
    };

    const response = await fetch('/api/plots', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const plot = await response.json();
      const item = document.createElement('div');
      item.className = 'plot-item';
      item.dataset.plotId = plot.id;
      item.innerHTML = `
        <div class="plot-info">
          <strong>${plot.name}</strong>
          <p>${plot.gardener} · ${plot.crop}</p>
          <small>${plot.season} · ${plot.rotation}</small>
        </div>
        <div class="plot-actions">
          <span class="badge">${plot.status}</span>
          <button class="btn-delete" data-delete-plot="${plot.id}">×</button>
        </div>
      `;
      plotList.appendChild(item);
      plotForm.reset();
      setupDeleteButtons();
    }
  });

  // Gestion des tâches
  taskForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {
      title: taskForm.querySelector('[name="title"]').value.trim(),
      detail: taskForm.querySelector('[name="detail"]').value.trim(),
      priority: taskForm.querySelector('[name="priority"]').value,
      season: taskForm.querySelector('[name="season"]').value
    };

    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const task = await response.json();
      const item = document.createElement('li');
      item.dataset.taskId = task.id;
      item.innerHTML = `
        <div class="task-content">
          <strong>${task.title}</strong>
          <p>${task.detail}</p>
          <span class="priority">${task.priority} · ${task.season}</span>
        </div>
        <button class="btn-delete" data-delete-task="${task.id}">×</button>
      `;
      taskList.appendChild(item);
      taskForm.reset();
      setupDeleteButtons();
    }
  });

  // Gestion des récoltes
  harvestForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = {
      crop: harvestForm.querySelector('[name="crop"]').value.trim(),
      quantity: harvestForm.querySelector('[name="quantity"]').value.trim(),
      gardener: harvestForm.querySelector('[name="gardener"]').value.trim(),
      location: harvestForm.querySelector('[name="location"]').value.trim()
    };

    const response = await fetch('/api/harvests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const harvest = await response.json();
      const item = document.createElement('li');
      item.dataset.harvestId = harvest.id;
      item.innerHTML = `
        <div class="harvest-content">
          <strong>${harvest.crop}</strong>
          <p>${harvest.quantity} · ${harvest.location}</p>
          <span class="priority">${harvest.gardener}</span>
        </div>
        <button class="btn-distribute" data-distribute-harvest="${harvest.id}">✓</button>
      `;
      harvestList.appendChild(item);
      harvestForm.reset();
      setupDistributeButtons();
    }
  });

  // Configuration des boutons de suppression
  function setupDeleteButtons() {
    document.querySelectorAll('[data-delete-plot]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.deletePlot;
        if (confirm('Supprimer cette parcelle ?')) {
          await fetch(`/api/plots/${id}`, { method: 'DELETE' });
          btn.closest('.plot-item').remove();
        }
      });
    });

    document.querySelectorAll('[data-delete-task]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.deleteTask;
        if (confirm('Supprimer cette tâche ?')) {
          await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
          btn.closest('li').remove();
        }
      });
    });
  }

  // Configuration des boutons de distribution
  function setupDistributeButtons() {
    document.querySelectorAll('[data-distribute-harvest]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.dataset.distributeHarvest;
        await fetch(`/api/harvests/${id}`, { method: 'PUT' });
        btn.textContent = '✓';
        btn.disabled = true;
        btn.style.background = '#a7f3d0';
      });
    });
  }

  // Initialisation des boutons
  setupDeleteButtons();
  setupDistributeButtons();
});
