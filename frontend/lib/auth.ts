"use client";

import { createContext, useContext, useEffect, useState } from "react";

import { api } from "@/lib/api";
import { AuthResponse, User } from "@/types";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  login: (payload: { email: string; password: string }) => Promise<void>;
  register: (payload: { email: string; password: string; full_name: string }) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      const token = window.localStorage.getItem("gan-studio-token");
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const { data } = await api.get<User>("/auth/me");
        setUser(data);
      } catch {
        window.localStorage.removeItem("gan-studio-token");
      } finally {
        setLoading(false);
      }
    };
    void bootstrap();
  }, []);

  const storeAuth = (data: AuthResponse) => {
    window.localStorage.setItem("gan-studio-token", data.access_token);
    setUser(data.user);
  };

  const login = async (payload: { email: string; password: string }) => {
    const { data } = await api.post<AuthResponse>("/auth/login", payload);
    storeAuth(data);
  };

  const register = async (payload: { email: string; password: string; full_name: string }) => {
    const { data } = await api.post<AuthResponse>("/auth/register", payload);
    storeAuth(data);
  };

  const logout = () => {
    window.localStorage.removeItem("gan-studio-token");
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

