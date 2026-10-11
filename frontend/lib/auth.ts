"use client";

import { useEffect, useState } from "react";
import { api } from "./api";

const TOKEN_KEY = "ai_deal_access_token";
const ROLE_KEY = "ai_deal_user_role";
const EMAIL_KEY = "ai_deal_user_email";

export type UserRole = "admin" | "sales" | "architect" | "ba" | "delivery" | "reviewer" | "viewer";

export type AuthUser = {
  email: string;
  role: UserRole;
};

export function getStoredToken() {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(TOKEN_KEY) || "";
}

export function setStoredToken(token: string) {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const role = window.localStorage.getItem(ROLE_KEY) as UserRole | null;
  const email = window.localStorage.getItem(EMAIL_KEY);
  return role && email ? { role, email } : null;
}

export function setStoredUser(user: AuthUser | null) {
  if (typeof window === "undefined") return;
  if (!user) {
    window.localStorage.removeItem(ROLE_KEY);
    window.localStorage.removeItem(EMAIL_KEY);
    return;
  }
  window.localStorage.setItem(ROLE_KEY, user.role);
  window.localStorage.setItem(EMAIL_KEY, user.email);
}

export function clearAuth() {
  setStoredToken("");
  setStoredUser(null);
}

export function useAuthToken() {
  const [token, setTokenState] = useState("");
  const [user, setUserState] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    setTokenState(getStoredToken());
    setUserState(getStoredUser());
    setReady(true);
  }, []);
  useEffect(() => {
    if (!ready || !token || user) return;
    api("/auth/me", {}, token)
      .then((result) => {
        const next = { email: result.user.email, role: result.user.role as UserRole };
        setStoredUser(next);
        setUserState(next);
      })
      .catch(() => {
        clearAuth();
        setTokenState("");
        setUserState(null);
      });
  }, [ready, token, user]);
  function setToken(next: string) {
    setStoredToken(next);
    setTokenState(next);
  }
  function setUser(next: AuthUser | null) {
    setStoredUser(next);
    setUserState(next);
  }
  return { ready, token, setToken, user, setUser };
}
