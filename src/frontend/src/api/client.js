const API_BASE = import.meta.env.VITE_API_URL || '';

function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
  };
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Ошибка авторизации');
  }
  return res.json();
}

export async function registerAdmin(username, password) {
  const res = await fetch(`${API_BASE}/api/auth/register-admin`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Ошибка регистрации');
  }
  return res.json();
}

export async function getMe(token) {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Не удалось загрузить профиль');
  return res.json();
}

export async function createUser(token, data) {
  const res = await fetch(`${API_BASE}/api/admin/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Ошибка создания пользователя');
  }
  return res.json();
}

export async function uploadPredict(token, file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/api/predict/upload`, {
    method: 'POST',
    headers: authHeaders(token),
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Ошибка загрузки файла');
  }
  return res.json();
}

export async function getTrainingHistory(token) {
  const res = await fetch(`${API_BASE}/api/analytics/training-history`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Ошибка загрузки истории обучения');
  return res.json();
}

export async function getClassDistribution(token) {
  const res = await fetch(`${API_BASE}/api/analytics/class-distribution`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Ошибка загрузки распределения классов');
  return res.json();
}

export async function getTopClasses(token) {
  const res = await fetch(`${API_BASE}/api/analytics/top-classes`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Ошибка загрузки топ классов');
  return res.json();
}

export async function getTestAccuracy(token) {
  const res = await fetch(`${API_BASE}/api/analytics/test-accuracy`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Ошибка загрузки результатов теста');
  return res.json();
}
