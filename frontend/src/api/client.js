const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function request(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

export const api = {
  register: (payload) => request("/api/auth/register", { method: "POST", body: payload }),
  login: (payload) => request("/api/auth/login", { method: "POST", body: payload }),
  me: (token) => request("/api/auth/me", { token }),
  challenges: (token) => request("/api/challenges", { token }),
  challenge: (token, id) => request(`/api/challenges/${id}`, { token }),
  submitFlag: (token, id, flag) =>
    request(`/api/challenges/${id}/submit`, { method: "POST", body: { flag }, token }),
  getHint: (token, id, question, hint_level) =>
    request(`/api/hints/${id}`, { method: "POST", body: { question, hint_level }, token }),
  cves: (token) => request("/api/cve", { token }),
  leaderboard: (token) => request("/api/leaderboard", { token }),
};
