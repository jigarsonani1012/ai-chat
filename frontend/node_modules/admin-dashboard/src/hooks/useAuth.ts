import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import type { AuthState } from "../types";

const STORAGE_KEY = "ai-chatbot-admin-auth";

export function useAuth() {
  const [auth, setAuth] = useState<AuthState | null>(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored ? (JSON.parse(stored) as AuthState) : null;
  });

  useEffect(() => {
    if (auth) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
    } else {
      window.localStorage.removeItem(STORAGE_KEY);
    }
  }, [auth]);

  async function login(email: string, password: string) {
    const result = await apiRequest<AuthState>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setAuth(result);
  }

  async function signup(organization_name: string, full_name: string, email: string, password: string) {
    const result = await apiRequest<AuthState>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ organization_name, full_name, email, password }),
    });
    setAuth(result);
  }

  function logout() {
    setAuth(null);
  }

  return { auth, login, signup, logout };
}
