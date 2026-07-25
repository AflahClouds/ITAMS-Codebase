import { createContext, useContext, useState } from 'react';
import AxiosInstance from './api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });

  const login = async (username, password) => {
    const res = await AxiosInstance.post('/auth/login/', { username, password });
    localStorage.setItem('token', res.data.token);
    localStorage.setItem('user', JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data.user;
  };

  const logout = async () => {
    try {
      await AxiosInstance.post('/auth/logout/');
    } catch {
      // token may already be invalid; clear locally regardless
    }
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const setToken = (token) => {
    localStorage.setItem('token', token);
  };

  const can = (code) => {
    if (!user) return false;
    if (user.is_admin) return true;
    return (user.permissions || []).includes(code);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, can, setToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
