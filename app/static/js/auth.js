// Shared auth utilities for frontend

export function saveAuth({ access, refresh, user }) {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
  localStorage.setItem('user', JSON.stringify(user));
}

export function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
}

export function getAuth() {
  const access = localStorage.getItem('access_token');
  const refresh = localStorage.getItem('refresh_token');
  const user = localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')) : null;
  return { access, refresh, user };
}

export async function authFetch(url, options = {}) {
  const { access } = getAuth();
  const headers = options.headers || {};
  if (access) headers['X-Auth-Token'] = access;
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401 && localStorage.getItem('refresh_token')) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers['X-Auth-Token'] = localStorage.getItem('access_token');
      return fetch(url, { ...options, headers });
    }
  }
  return res;
}

export async function tryRefresh() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  const res = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: refresh })
  });
  if (!res.ok) { clearAuth(); return false; }
  const data = await res.json();
  saveAuth({ access: data.access_token, refresh: data.refresh_token, user: getAuth().user });
  return true;
}
