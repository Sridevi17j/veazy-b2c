'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useMemo } from 'react';

interface User {
  id: string;
  phone_number: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  preferred_name?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
  getAuthHeaders: () => { [key: string]: string };
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Helper function to get stored token
  const getStoredToken = (): string | null => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  };

  // Helper function to store token
  const storeToken = (token: string): void => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  };

  // Helper function to remove token
  const removeToken = (): void => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  };

  // Helper function to get auth headers
  const getAuthHeaders = (): { [key: string]: string } => {
    const token = getStoredToken();
    const headers: { [key: string]: string } = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  };

  const checkAuth = useCallback(async (): Promise<boolean> => {
    try {
      const token = getStoredToken();
      if (!token) {
        setUser(null);
        return false;
      }

      const response = await fetch('http://localhost:8000/api/auth/session', {
      // const response = await fetch('https://veazy-backend.onrender.com/api/auth/session', {
        headers: getAuthHeaders(),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Session response:', data); // Debug log
        if (data.success && data.user_id) {
          setUser({
            id: data.user_id,
            phone_number: data.phone_number,
            first_name: data.first_name,
            last_name: data.last_name,
            email: data.email,
            preferred_name: data.preferred_name,
          });
          return true;
        }
      } else {
        console.log('Session check failed with status:', response.status);
        const errorData = await response.text();
        console.log('Error response:', errorData);
      }
      
      setUser(null);
      return false;
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      return false;
    }
  }, []);

  const login = (userData: User, token: string) => {
    setUser(userData);
    storeToken(token);
  };

  const logout = useCallback(async () => {
    try {
      await fetch('http://localhost:8000/api/auth/logout', {
      // await fetch('https://veazy-backend.onrender.com/api/auth/logout', {
        method: 'POST',
        headers: getAuthHeaders(),
      });
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      removeToken();
      setUser(null);
    }
  }, []);

  // Check authentication on mount
  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      await checkAuth();
      setIsLoading(false);
    };

    initAuth();
  }, [checkAuth]);

  const value: AuthContextType = useMemo(() => ({
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    checkAuth,
    getAuthHeaders,
  }), [user, isLoading, logout, checkAuth]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}