const API = '/api';

function getToken() { return localStorage.getItem('token') || ''; }
function setToken(token) { localStorage.setItem('token', token); }
function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...authHeaders(), ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || 'Ошибка запроса');
  return data;
}

async function renderNews(containerId) {
  const target = document.getElementById(containerId);
  if (!target) return;
  const news = await api('/news');
  target.innerHTML = news.map(n => `<article class="card fade"><h3>${n.title}</h3><p>${n.summary}</p></article>`).join('');
}

async function renderSpecialties(containerId) {
  const target = document.getElementById(containerId);
  if (!target) return;
  const items = await api('/specialties');
  target.innerHTML = items.map(s => `<article class="card fade"><h3>${s.title}</h3><p><b>${s.code}</b> • ${s.duration}</p><p>${s.description}</p></article>`).join('');
}

async function renderTeachers(containerId) {
  const target = document.getElementById(containerId);
  if (!target) return;
  const items = await api('/teachers');
  target.innerHTML = items.map(t => `<article class="card fade"><h3>${t.full_name}</h3><p>${t.position}</p><p>${t.bio}</p><small>${t.email}</small></article>`).join('');
}

async function renderSchedule(tableId) {
  const body = document.getElementById(tableId);
  if (!body) return;
  const items = await api('/schedule');
  body.innerHTML = items.map(s => `<tr><td>${s.group_name}</td><td>${s.day_of_week}</td><td>${s.lesson_time}</td><td>${s.subject}</td><td>${s.teacher}</td><td>${s.room}</td></tr>`).join('');
}

async function renderContacts(containerId) {
  const target = document.getElementById(containerId);
  if (!target) return;
  const c = await api('/contacts');
  target.innerHTML = `<div class="card"><p><b>Адрес:</b> ${c.address}</p><p><b>Телефон:</b> ${c.phone}</p><p><b>Email:</b> ${c.email}</p><a class="btn" target="_blank" href="${c.map_embed}">Открыть карту</a></div>`;
}

async function initAuthForms() {
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const form = new FormData(loginForm);
      try {
        const data = await api('/auth/login', { method: 'POST', body: JSON.stringify({ email: form.get('email'), password: form.get('password') }) });
        setToken(data.access_token);
        location.href = '/pages/student-cabinet.html';
      } catch (err) { alert(err.message); }
    });
  }

  const regForm = document.getElementById('registerForm');
  if (regForm) {
    regForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const form = new FormData(regForm);
      const payload = Object.fromEntries(form.entries());
      try {
        await api('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
        alert('Регистрация завершена. Теперь войдите.');
      } catch (err) { alert(err.message); }
    });
  }
}

async function initApplicationForm() {
  const formEl = document.getElementById('applicationForm');
  if (!formEl) return;
  const spec = await api('/specialties');
  document.getElementById('specialtyId').innerHTML = spec.map(s => `<option value="${s.id}">${s.title}</option>`).join('');
  formEl.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(formEl).entries());
    payload.specialty_id = Number(payload.specialty_id);
    await api('/applications', { method: 'POST', body: JSON.stringify(payload) });
    alert('Заявка отправлена!');
    formEl.reset();
  });
}

async function initStudentDashboard() {
  const root = document.getElementById('studentDashboard');
  if (!root) return;
  try {
    const data = await api('/student/dashboard');
    root.innerHTML = `<div class="notice">${data.profile.full_name} (${data.profile.group_name})</div>
      <h3>Моё расписание</h3><ul>${data.schedule.map(s=>`<li>${s.day_of_week} ${s.lesson_time} — ${s.subject}</li>`).join('')}</ul>
      <h3>Новости</h3><ul>${data.news.map(n=>`<li>${n.title}</li>`).join('')}</ul>`;
  } catch {
    root.innerHTML = '<p>Требуется вход. Используйте логин student@college.local / student123.</p>';
  }
}

async function initAdminPanel() {
  const form = document.getElementById('newsCreateForm');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(form).entries());
    try {
      await api('/admin/news', { method: 'POST', body: JSON.stringify(payload) });
      alert('Новость создана');
      form.reset();
    } catch (err) { alert('Нужен admin токен: ' + err.message); }
  });
}

window.addEventListener('DOMContentLoaded', () => {
  renderNews('newsList').catch(() => {});
  renderSpecialties('specialtiesList').catch(() => {});
  renderTeachers('teachersList').catch(() => {});
  renderSchedule('scheduleBody').catch(() => {});
  renderContacts('contactsBox').catch(() => {});
  initAuthForms();
  initApplicationForm().catch(() => {});
  initStudentDashboard().catch(() => {});
  initAdminPanel();
});
