import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getCurrentUser, login as apiLogin, register as apiRegister } from '../api/auth';
import { getToken, setToken, removeToken } from '../utils/token';

interface User {
  id: number;
  username: string;
  is_admin: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = useCallback(() => {
    removeToken();
    setUser(null);
  }, []);

  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      try {
        const token = getToken();
        if (!token) {
          if (isMounted) {
            setLoading(false);
          }
          return;
        }

        const u = await getCurrentUser();
        if (isMounted) {
          setUser(u);
        }
      } catch (error: any) {
        console.log('Auth initialization failed:', error);
        // 如果是 401 错误，清除无效的 token
        if (error?.response?.status === 401) {
          removeToken();
        }
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    initAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (username: string, password: string) => {
    const { access_token } = await apiLogin(username, password);
    setToken(access_token);
    const u = await getCurrentUser();
    setUser(u);
  };

  const register = async (username: string, password: string) => {
    await apiRegister(username, password);
    await login(username, password);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAdmin: !!user?.is_admin }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);