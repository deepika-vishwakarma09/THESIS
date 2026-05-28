
// src/context/AuthContext.js
// ───────────────────────────
// Manages login/logout state across all screens
 
import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { registerUser, loginUser } from '../services/api';
 
const AuthContext = createContext();
 
export const AuthProvider = ({ children }) => {
  const [user, setUser]       = useState(null);
  const [token, setToken]     = useState(null);
  const [loading, setLoading] = useState(true);
 
  // ── Load saved token on app start ──────────────────────
  useEffect(() => {
    loadStoredAuth();
  }, []);
 
  const loadStoredAuth = async () => {
    try {
      const savedToken = await AsyncStorage.getItem('token');
      const savedUser  = await AsyncStorage.getItem('user');
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      }
    } catch (e) {
      console.log('Auth load error:', e);
    } finally {
      setLoading(false);
    }
  };
 
  // ── Register ────────────────────────────────────────────
  const register = async (username, email, password) => {
    const data = await registerUser(username, email, password);
    await AsyncStorage.setItem('token', data.access_token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };
 
  // ── Login ───────────────────────────────────────────────
  const login = async (username, password) => {
    const data = await loginUser(username, password);
    await AsyncStorage.setItem('token', data.access_token);
    await AsyncStorage.setItem('user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };
 
  // ── Logout ──────────────────────────────────────────────
  const logout = async () => {
    await AsyncStorage.removeItem('token');
    await AsyncStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };
 
  return (
    <AuthContext.Provider value={{ user, token, loading, register, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
 
export const useAuth = () => useContext(AuthContext);