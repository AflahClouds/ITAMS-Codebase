import { useState } from 'react';
import AxiosInstance from './api/client';
import { AuthContext } from './auth/context';

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

  // Mirrors the backend's own-records scope so the menu does not offer pages that
  // will answer 403. The backend remains the authorization boundary.
  const hasOwnRecordsScope = () => user?.role === 'Employee';

  return (
    <AuthContext.Provider value={{ user, login, logout, can, hasOwnRecordsScope, setToken }}>
      {children}
    </AuthContext.Provider>
  );
}
