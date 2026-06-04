function todayISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function toast(msg) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2000);
}

async function api(url, opts = {}) {
  const localDate = todayISO();
  let fetchUrl = url;
  if (!url.includes('date=')) {
    fetchUrl += (url.includes('?') ? '&' : '?') + `date=${localDate}`;
  }
  const res = await fetch(fetchUrl, {
    headers: {
      'Content-Type': 'application/json',
      'X-Local-Date': localDate,
      ...opts.headers,
    },
    ...opts,
  });
  return res.json();
}

function closeModal(id) {
  document.getElementById(id)?.classList.remove('open');
}

async function mergeFoodToday(patch) {
  const data = await api(`/api/food?date=${todayISO()}`);
  const f = data.food || {};
  const d = data.daily || {};
  await api('/api/food', {
    method: 'POST',
    body: JSON.stringify({
      log_date: todayISO(),
      calories: patch.calories ?? f.calories ?? null,
      protein_g: patch.protein_g ?? f.protein_g ?? null,
      carbs_g: f.carbs_g ?? null,
      fat_g: f.fat_g ?? null,
      water_liters: patch.water_liters ?? f.water_liters ?? d.water_liters ?? null,
      steps: patch.steps ?? d.steps ?? null,
      sleep_hours: d.sleep_hours ?? null,
      daily_notes: d.notes || f.notes || '',
    }),
  });
}

async function loadDashboard() {
  const data = await api('/api/dashboard');
  const loading = document.getElementById('dashboard-loading');
  const panel = document.getElementById('dashboard');
  if (!panel) return;
  if (loading) loading.style.display = 'none';
  panel.style.display = 'block';

  document.getElementById('day-name').textContent = data.day_name;
  document.getElementById('muscle-group').textContent = data.muscle_group || '';
  const badge = document.getElementById('rest-badge');
  if (badge) badge.style.display = data.is_rest_day ? 'inline' : 'none';

  const plan = document.getElementById('today-plan');
  if (plan) {
    plan.innerHTML = '';
    (data.plan || []).forEach((p) => {
      const li = document.createElement('li');
      li.innerHTML = `<span>${p.exercise_name}</span><span class="sets">${p.sets_target}×${p.reps_target}</span>`;
      plan.appendChild(li);
    });
  }

  const qw = document.getElementById('q-weight');
  if (qw && data.current_weight) qw.value = data.current_weight;
  const qc = document.getElementById('q-cal');
  if (qc && data.calories) qc.value = data.calories;
  const qp = document.getElementById('q-protein');
  if (qp && data.protein) qp.value = data.protein;
  const qs = document.getElementById('q-steps');
  if (qs && data.steps) qs.value = data.steps;

  document.getElementById('current-weight').textContent = data.current_weight ?? '—';
  document.getElementById('goal-weight').textContent = data.goal_weight ?? '—';
  document.getElementById('progress-pct').textContent = `${data.progress_percent ?? 0}%`;
  document.getElementById('progress-fill').style.width = `${data.progress_percent || 0}%`;

  const pace = document.getElementById('pace-msg');
  if (pace) {
    pace.textContent = data.pace_message || '';
    pace.className = `pace-${(data.pace_status || 'unknown').replace('too_', '')} caption`;
  }

  document.getElementById('cal-in').textContent = data.calories ?? '—';
  document.getElementById('protein').textContent = data.protein ?? '—';
  document.getElementById('cardio-min').textContent = Math.round(data.cardio_minutes || 0);
  document.getElementById('swim-min').textContent = Math.round(data.swimming_minutes || 0);
  document.getElementById('cal-burn').textContent = data.calories_burned_estimate ?? 0;
  document.getElementById('deficit').textContent = data.estimated_deficit ?? '—';
}

async function quickSave(type) {
  const t = todayISO();
  try {
    if (type === 'weight') {
      const v = parseFloat(document.getElementById('q-weight').value);
      if (!v) return toast('Enter weight');
      await api('/api/weight', { method: 'POST', body: JSON.stringify({ log_date: t, weight_kg: v }) });
    } else if (type === 'cal') {
      const v = parseFloat(document.getElementById('q-cal').value);
      if (!v) return toast('Enter calories');
      await mergeFoodToday({ calories: v });
    } else if (type === 'protein') {
      const v = parseFloat(document.getElementById('q-protein').value);
      if (!v) return toast('Enter protein');
      await mergeFoodToday({ protein_g: v });
    } else if (type === 'bike') {
      const v = parseFloat(document.getElementById('q-bike').value);
      if (!v) return toast('Enter minutes');
      await api('/api/cardio', {
        method: 'POST',
        body: JSON.stringify({ log_date: t, cardio_type: 'bicycle', duration_minutes: v, intensity: 'moderate' }),
      });
    } else if (type === 'swim') {
      const v = parseFloat(document.getElementById('q-swim').value);
      if (!v) return toast('Enter minutes');
      await api('/api/swimming', {
        method: 'POST',
        body: JSON.stringify({ log_date: t, swimming_minutes: v, intensity: 'moderate' }),
      });
    } else if (type === 'steps') {
      const v = parseInt(document.getElementById('q-steps').value, 10);
      if (!v) return toast('Enter steps');
      await mergeFoodToday({ steps: v });
    }
    toast('Saved');
    loadDashboard();
  } catch {
    toast('Error saving');
  }
}

let weightChart = null;

async function saveWeightQuick() {
  const v = parseFloat(document.getElementById('weight-kg').value);
  if (!v) return toast('Enter weight');
  await api('/api/weight', {
    method: 'POST',
    body: JSON.stringify({ log_date: todayISO(), weight_kg: v }),
  });
  toast('Saved');
  loadWeightHistory();
}

async function initWeightPage() {
  const dash = await api('/api/dashboard');
  const inp = document.getElementById('weight-kg');
  if (inp && dash.current_weight) inp.value = dash.current_weight;
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
  document.getElementById('workout-muscle').textContent =
    `${data.plan?.[0]?.muscle_group || ''} · tap Save per exercise`;

  const list = document.getElementById('exercise-list');
  const empty = document.getElementById('workout-empty');
  list.innerHTML = '';

  if (!data.exercises?.length) {
    empty.style.display = 'block';
    return;
  }
  empty.style.display = 'none';

  data.exercises.forEach((ex) => {
    const row = document.createElement('div');
    row.className = 'card card-compact';
    const last = ex.last_weight_kg != null
      ? `Last ${ex.last_weight_kg} kg × ${ex.last_reps || '?'}`
      : '';
    const logged = (ex.sets_logged || []).find((x) => x.completed) || ex.sets_logged?.[0] || {};
    row.innerHTML = `
      <div class="quick-row quick-row-ex">
        <span class="ex-name">${ex.exercise_name}</span>
        <input type="number" step="0.5" class="w-kg" placeholder="kg" value="${logged.weight_kg ?? ex.last_weight_kg ?? ''}">
        <input type="number" class="w-reps" placeholder="reps" value="${logged.reps ?? ''}">
        <button type="button" class="btn-save w-save">Save</button>
        ${last ? `<span class="ex-last">${last} · ${ex.sets_target}×${ex.reps_target}</span>` : ''}
      </div>`;
    list.appendChild(row);

    let setNum = (ex.sets_logged?.length || 0) + 1;
    row.querySelector('.w-save').onclick = async () => {
      const kg = parseFloat(row.querySelector('.w-kg').value) || null;
      const reps = parseInt(row.querySelector('.w-reps').value, 10) || null;
      await api('/api/workout/set', {
        method: 'POST',
        body: JSON.stringify({
          session_id: data.session_id,
          exercise_name: ex.exercise_name,
          set_number: Math.min(setNum, ex.sets_target || 4),
          weight_kg: kg,
          reps,
          completed: true,
          notes: '',
        }),
      });
      setNum += 1;
      toast(`${ex.exercise_name} saved`);
    };
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

function valOrNull(id, parser) {
  const el = document.getElementById(id);
  if (!el || el.value === '') return null;
  return parser(el.value);
}

async function initFoodPage() {
  const data = await api(`/api/food?date=${todayISO()}`);
  const f = data.food || {};
  const daily = data.daily || {};
  const set = (id, v) => { const el = document.getElementById(id); if (el && v != null) el.value = v; };
  set('food-cal', f.calories);
  set('food-protein', f.protein_g);
  set('food-carbs', f.carbs_g);
  set('food-fat', f.fat_g);
  set('food-water', f.water_liters ?? daily.water_liters);
  set('food-steps', daily.steps);
  set('food-sleep', daily.sleep_hours);
  set('food-notes', [f.notes, daily.notes].filter(Boolean).join(' '));
}

async function saveFoodQuick() {
  await api('/api/food', {
    method: 'POST',
    body: JSON.stringify({
      log_date: todayISO(),
      calories: valOrNull('food-cal', parseFloat),
      protein_g: valOrNull('food-protein', parseFloat),
      carbs_g: valOrNull('food-carbs', parseFloat),
      fat_g: valOrNull('food-fat', parseFloat),
      water_liters: valOrNull('food-water', parseFloat),
      steps: valOrNull('food-steps', (x) => parseInt(x, 10)),
      sleep_hours: valOrNull('food-sleep', parseFloat),
      daily_notes: document.getElementById('food-notes')?.value || '',
    }),
  });
  toast('Saved');
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

const LANG_STORAGE_KEY = 'gym_lang';

function getSavedLang() {
  return localStorage.getItem(LANG_STORAGE_KEY) || 'en';
}

function saveLang(lang) {
  localStorage.setItem(LANG_STORAGE_KEY, lang);
}

async function loadCoursePlan(lang) {
  const data = await api(`/api/course-plan?lang=${lang}`);
  const root = document.getElementById('plan-root');
  const ui = data.ui;
  root.dir = data.dir;
  root.classList.toggle('rtl', data.dir === 'rtl');
  document.documentElement.lang = data.lang;
  document.getElementById('lang-label').textContent = ui.language;
  document.querySelector('header.app-header h1').textContent = ui.page_title;
  document.getElementById('plan-subtitle').textContent = ui.subtitle;
  document.getElementById('nutrition-title').textContent = ui.nutrition_title;
  document.getElementById('nutrition-list').innerHTML = `
    <li>${ui.nutrition_cal}</li>
    <li>${ui.nutrition_protein}</li>
    <li>${ui.nutrition_water}</li>
    <li>${ui.nutrition_steps}</li>`;
  document.getElementById('rest-note').textContent = ui.rest_note;

  const daysEl = document.getElementById('plan-days');
  daysEl.innerHTML = '';
  data.days.forEach((day) => {
    const card = document.createElement('div');
    card.className = `card course-day${day.is_rest ? ' rest-day' : ''}`;
    let list = '';
    day.exercises.forEach((ex) => {
      const tag = ex.tag_label
        ? `<span class="ex-tag ${ex.tag || ''}">${ex.tag_label}</span>`
        : '';
      list += `<li><span>${ex.name}${tag}</span><span class="sets">${ex.detail}</span></li>`;
    });
    const restHint = day.is_rest ? `<p class="day-summary">${ui.friday_rest}</p>` : '';
    card.innerHTML = `
      <h2>${day.day_name} <span class="badge">${day.muscle_group}</span></h2>
      <p class="day-summary">${day.summary}</p>
      ${restHint}
      <ul class="checklist">${list}</ul>`;
    daysEl.appendChild(card);
  });
}

function initCoursePlanPage() {
  const select = document.getElementById('lang-select');
  if (!select) return;
  const saved = getSavedLang();
  select.value = saved;
  loadCoursePlan(saved);
  select.addEventListener('change', () => {
    saveLang(select.value);
    loadCoursePlan(select.value);
  });
}
