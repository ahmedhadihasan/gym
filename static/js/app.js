function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function toast(msg) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2000);
}

async function api(url, opts = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  });
  return res.json();
}

function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
}

async function loadDashboard() {
  const data = await api('/api/dashboard');
  document.getElementById('dashboard-loading').style.display = 'none';
  document.getElementById('dashboard').style.display = 'block';

  document.getElementById('day-name').textContent = data.day_name;
  document.getElementById('muscle-group').textContent = data.muscle_group || '';
  if (data.is_rest_day) {
    document.getElementById('rest-badge').style.display = 'inline';
  }

  const plan = document.getElementById('today-plan');
  plan.innerHTML = '';
  (data.plan || []).forEach((p) => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${p.exercise_name}</span><span class="sets">${p.sets_target}x ${p.reps_target}</span>`;
    plan.appendChild(li);
  });

  document.getElementById('current-weight').textContent = data.current_weight ?? '—';
  document.getElementById('goal-weight').textContent = data.goal_weight ?? '—';
  document.getElementById('progress-pct').textContent = data.progress_percent ?? 0;
  document.getElementById('progress-fill').style.width = `${data.progress_percent || 0}%`;
  document.getElementById('avg-7').textContent = data.weight_7day_avg ?? '—';

  const pace = document.getElementById('pace-msg');
  pace.textContent = data.pace_message || '';
  pace.className = `pace-${(data.pace_status || 'unknown').replace('too_', '')}`;

  document.getElementById('cal-in').textContent = data.calories ?? '—';
  document.getElementById('protein').textContent = data.protein ?? '—';
  document.getElementById('cardio-min').textContent = Math.round(data.cardio_minutes || 0);
  document.getElementById('swim-min').textContent = Math.round(data.swimming_minutes || 0);
  document.getElementById('cal-burn').textContent = data.calories_burned_estimate ?? 0;
  document.getElementById('deficit').textContent = data.estimated_deficit ?? '—';
}

let weightChart = null;

async function initWeightPage() {
  document.getElementById('weight-date').value = todayISO();
  document.getElementById('weight-form').onsubmit = async (e) => {
    e.preventDefault();
    await api('/api/weight', {
      method: 'POST',
      body: JSON.stringify({
        log_date: document.getElementById('weight-date').value,
        weight_kg: parseFloat(document.getElementById('weight-kg').value),
      }),
    });
    toast('Weight saved');
    loadWeightHistory();
  };
  loadWeightHistory();
}

async function loadWeightHistory() {
  const data = await api('/api/weight');
  document.getElementById('avg-7-display').textContent = data.avg_7day ?? '—';

  const hist = document.getElementById('weight-history');
  hist.innerHTML = '';
  (data.history || []).slice(0, 14).forEach((r) => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${r.log_date}</span><span>${r.weight_kg} kg</span>`;
    hist.appendChild(li);
  });

  const chartData = [...(data.history || [])].reverse();
  const ctx = document.getElementById('weight-chart');
  if (!ctx) return;
  if (weightChart) weightChart.destroy();
  weightChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartData.map((d) => d.log_date.slice(5)),
      datasets: [{
        label: 'kg',
        data: chartData.map((d) => d.weight_kg),
        borderColor: '#3fb950',
        backgroundColor: 'rgba(63, 185, 80, 0.15)',
        fill: true,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
        y: { ticks: { color: '#8b949e' }, grid: { color: '#30363d' } },
      },
    },
  });
}

async function initWorkoutPage() {
  const data = await api('/api/workout/today');
  document.getElementById('workout-day').textContent = data.day_name;
  document.getElementById('workout-muscle').textContent = data.plan?.[0]?.muscle_group || '';

  const list = document.getElementById('exercise-list');
  const empty = document.getElementById('workout-empty');
  list.innerHTML = '';

  if (!data.exercises?.length) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  data.exercises.forEach((ex) => {
    if (!ex.is_weight_exercise && ex.sets_target <= 1) return;

    const card = document.createElement('div');
    card.className = 'card exercise-card';
    const sets = ex.sets_target || 3;
    const last = ex.last_weight_kg != null
      ? `Last: ${ex.last_weight_kg} kg × ${ex.last_reps || '?'} reps`
      : 'No previous weight';

    let setsHtml = '';
    for (let s = 1; s <= sets; s++) {
      const logged = (ex.sets_logged || []).find((x) => x.set_number === s) || {};
      setsHtml += `
        <div class="set-row" data-set="${s}">
          <div><label>Set ${s}</label><input type="number" step="0.5" class="set-weight" value="${logged.weight_kg ?? ''}" placeholder="kg"></div>
          <div><label>Reps</label><input type="number" class="set-reps" value="${logged.reps ?? ''}"></div>
          <div><label>Done</label><input type="checkbox" class="set-done" ${logged.completed ? 'checked' : ''} style="width:44px;height:44px"></div>
          <button type="button" class="btn btn-secondary save-set-btn" style="width:auto;padding:0 12px;margin:0">✓</button>
        </div>`;
    }

    card.innerHTML = `
      <h2>${ex.exercise_name}</h2>
      <p class="last-weight">${last} · Target: ${ex.sets_target}×${ex.reps_target}</p>
      ${setsHtml}
      <label>Notes</label>
      <input type="text" class="ex-notes" placeholder="Form, back pain, etc.">
    `;
    list.appendChild(card);

    card.querySelectorAll('.save-set-btn').forEach((btn) => {
      btn.onclick = async () => {
        const row = btn.closest('.set-row');
        const sn = parseInt(row.dataset.set, 10);
        const notes = card.querySelector('.ex-notes').value;
        await api('/api/workout/set', {
          method: 'POST',
          body: JSON.stringify({
            session_id: data.session_id,
            exercise_name: ex.exercise_name,
            set_number: sn,
            weight_kg: parseFloat(row.querySelector('.set-weight').value) || null,
            reps: parseInt(row.querySelector('.set-reps').value, 10) || null,
            completed: row.querySelector('.set-done').checked,
            notes,
          }),
        });
        card.classList.add('done');
        toast(`Set ${sn} saved`);
      };
    });
  });
}

async function saveCardio(e) {
  e.preventDefault();
  const steps = document.getElementById('cardio-steps').value;
  let notes = document.getElementById('cardio-notes').value;
  if (steps) notes = `Steps: ${steps}. ${notes}`.trim();

  const body = {
    log_date: document.getElementById('cardio-date').value,
    cardio_type: document.getElementById('cardio-type').value,
    duration_minutes: parseFloat(document.getElementById('cardio-mins').value),
    intensity: document.getElementById('cardio-intensity').value,
    calories_burned_estimate: document.getElementById('cardio-cal').value || null,
    notes,
  };
  const res = await api('/api/cardio', { method: 'POST', body: JSON.stringify(body) });
  toast(`Saved · ~${res.calories_estimate} kcal`);
  if (steps) {
    await api('/api/food', {
      method: 'POST',
      body: JSON.stringify({
        log_date: body.log_date,
        steps: parseInt(steps, 10),
      }),
    });
  }
  e.target.reset();
  document.getElementById('cardio-date').value = body.log_date;
  loadCardioToday();
}

async function loadCardioToday() {
  const date = document.getElementById('cardio-date')?.value || todayISO();
  const rows = await api(`/api/cardio?date=${date}`);
  const ul = document.getElementById('cardio-today');
  if (!ul) return;
  ul.innerHTML = rows.length ? '' : '<li>No logs yet</li>';
  rows.forEach((r) => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${r.cardio_type} ${r.duration_minutes}min</span><span>${r.calories_burned_estimate || 0} kcal</span>`;
    ul.appendChild(li);
  });
}

async function saveSwimming(e) {
  e.preventDefault();
  const body = {
    log_date: document.getElementById('swim-date').value,
    swimming_minutes: parseFloat(document.getElementById('swim-mins').value),
    intensity: document.getElementById('swim-intensity').value,
    calories_burned_estimate: document.getElementById('swim-cal').value || null,
    notes: document.getElementById('swim-notes').value,
  };
  const res = await api('/api/swimming', { method: 'POST', body: JSON.stringify(body) });
  toast(`Saved · ~${res.calories_estimate} kcal`);
  loadSwimToday();
}

async function loadSwimToday() {
  const date = document.getElementById('swim-date')?.value || todayISO();
  const rows = await api(`/api/swimming?date=${date}`);
  const ul = document.getElementById('swim-today');
  if (!ul) return;
  ul.innerHTML = rows.length ? '' : '<li>No logs yet</li>';
  rows.forEach((r) => {
    const li = document.createElement('li');
    li.innerHTML = `<span>${r.swimming_minutes} min (${r.intensity})</span><span>${r.calories_burned_estimate || 0} kcal</span>`;
    ul.appendChild(li);
  });
}

async function loadFood() {
  const d = document.getElementById('food-date').value;
  const data = await api(`/api/food?date=${d}`);
  const f = data.food || {};
  const daily = data.daily || {};
  document.getElementById('food-cal').value = f.calories ?? '';
  document.getElementById('food-protein').value = f.protein_g ?? '';
  document.getElementById('food-carbs').value = f.carbs_g ?? '';
  document.getElementById('food-fat').value = f.fat_g ?? '';
  document.getElementById('food-water').value = f.water_liters ?? daily.water_liters ?? '';
  document.getElementById('food-steps').value = daily.steps ?? '';
  document.getElementById('food-sleep').value = daily.sleep_hours ?? '';
  document.getElementById('food-notes').value = [f.notes, daily.notes].filter(Boolean).join(' ') || '';
}

async function saveFood(e) {
  e.preventDefault();
  const d = document.getElementById('food-date').value;
  await api('/api/food', {
    method: 'POST',
    body: JSON.stringify({
      log_date: d,
      calories: parseFloat(document.getElementById('food-cal').value) || null,
      protein_g: parseFloat(document.getElementById('food-protein').value) || null,
      carbs_g: parseFloat(document.getElementById('food-carbs').value) || null,
      fat_g: parseFloat(document.getElementById('food-fat').value) || null,
      water_liters: parseFloat(document.getElementById('food-water').value) || null,
      steps: parseInt(document.getElementById('food-steps').value, 10) || null,
      sleep_hours: parseFloat(document.getElementById('food-sleep').value) || null,
      daily_notes: document.getElementById('food-notes').value,
    }),
  });
  toast('Daily log saved');
}

async function loadWeeklyReport() {
  const data = await api('/api/report/weekly?days=7');
  document.getElementById('r-avg-w').textContent = data.average_weight ?? '—';
  document.getElementById('r-workouts').textContent = data.total_workouts ?? 0;
  document.getElementById('r-swim').textContent = Math.round(data.total_swimming_minutes || 0);
  document.getElementById('r-cardio').textContent = Math.round(data.total_cardio_minutes || 0);
  document.getElementById('r-cal').textContent = data.average_calories ?? '—';
  document.getElementById('r-prot').textContent = data.average_protein ?? '—';
}

async function exportCSV() {
  await api('/api/export-csv', { method: 'POST' });
  toast('CSV files exported to exports/');
}

async function importCSV() {
  const filename = document.getElementById('import-file').value;
  const res = await api('/api/import-csv', {
    method: 'POST',
    body: JSON.stringify({ filename }),
  });
  toast(res.message || (res.ok ? 'Imported' : 'Failed'));
  loadWeeklyReport();
}

async function chatGPTReport() {
  const res = await api('/api/chatgpt-report');
  document.getElementById('report-text').textContent = res.report;
  document.getElementById('report-modal').classList.add('open');
}

function copyReport() {
  const text = document.getElementById('report-text').textContent;
  navigator.clipboard.writeText(text).then(() => toast('Copied!'));
}
