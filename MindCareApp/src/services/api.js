// src/services/api.js
import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

// ── Web-safe token storage (localStorage for web) ─────────
const TokenStorage = {
  get: async () => {
    try { return localStorage.getItem('token'); } catch { return null; }
  },
  set: async (token) => {
    try { localStorage.setItem('token', token); } catch {}
  },
  remove: async () => {
    try { localStorage.removeItem('token'); } catch {}
  },
};

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Auto attach token
api.interceptors.request.use(async (config) => {
  const token = await TokenStorage.get();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── AUTH ──────────────────────────────────────────────────
export const registerUser = async (username, email, password) => {
  const res = await api.post('/api/auth/register', { username, email, password });
  await TokenStorage.set(res.data.access_token);
  return res.data;
};

export const loginUser = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  const res = await api.post('/api/auth/login', formData.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  await TokenStorage.set(res.data.access_token);
  return res.data;
};

export const getMe = async () => {
  const res = await api.get('/api/auth/me');
  return res.data;
};

export const logoutUser = async () => {
  await TokenStorage.remove();
};

// ── MOOD ──────────────────────────────────────────────────
export const logMood = async (mood_level, notes = '') => {
  const res = await api.post('/api/mood/log', { mood_level, notes });
  return res.data;
};

export const getMoodHistory = async () => {
  const res = await api.get('/api/mood/history');
  return res.data;
};

// ── CHAT ──────────────────────────────────────────────────
export const sendMessage = async (message, session_id = null, selected_mood = null, mood_level = null) => {
  const res = await api.post('/api/chat/send', {
    message, session_id, selected_mood, mood_level,
  });
  return res.data;
};

// ── ANALYSIS ──────────────────────────────────────────────
export const analyzeSession = async (session_id) => {
  const res = await api.post('/api/analyze/session', { session_id });
  return res.data;
};

// ── DASHBOARD ─────────────────────────────────────────────
export const getDashboard = async () => {
  const res = await api.get('/api/dashboard');
  return res.data;
};

export default api;