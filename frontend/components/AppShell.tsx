"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect } from "react";
import { Brand } from "./Brand";
import { Icon, type IconName } from "./Icon";
import { clearAuth, useAuthToken } from "../lib/auth";
import { can } from "../lib/rbac";

type NavItem = { label: string; href: string; match: string; icon: IconName };

function navItems(sessionId?: string): NavItem[] {
  const id = sessionId;
  return [
    { label: "Dashboard", href: "/dashboard", match: "/dashboard", icon: "dashboard" },
    { label: "Scoping Sessions", href: "/sessions", match: "/sessions", icon: "sessions" },
    { label: "Requirements", href: id ? `/requirements/${id}` : "/sessions", match: "/requirements", icon: "requirements" },
    { label: "PRD & Scope", href: id ? `/prd/${id}` : "/sessions", match: "/prd", icon: "prd" },
    { label: "Solution Design", href: id ? `/architecture/${id}` : "/sessions", match: "/architecture", icon: "design" },
    { label: "Data & AI", href: id ? `/data-ai/${id}` : "/sessions", match: "/data-ai", icon: "data" },
    { label: "Estimation", href: id ? `/estimate/${id}` : "/sessions", match: "/estimate", icon: "estimate" },
    { label: "Change Impact", href: id ? `/package/${id}` : "/sessions", match: "/package", icon: "change" },
    { label: "Validation & Export", href: id ? `/package/${id}` : "/sessions", match: "/package", icon: "export" },
  ];
}

function isActive(pathname: string, item: NavItem) {
  if (item.match === "/") return pathname === "/";
  return pathname.startsWith(item.match);
}

export function AppShell({ children, sessionId }: { children: ReactNode; sessionId?: string }) {
  const pathname = usePathname();
  const router = useRouter();
  const { ready, token, user } = useAuthToken();
  useEffect(() => {
    if (ready && !token) router.replace("/login");
  }, [ready, token, router]);
  if (!ready || !token) {
    return <main className="content">Loading...</main>;
  }
  const items = navItems(sessionId);
  const visibleItems = can(user?.role, "manageUsers")
    ? [...items, { label: "User Management", href: "/admin/users", match: "/admin/users", icon: "settings" as IconName }]
    : items;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Brand />
        <nav className="nav-list" aria-label="Main navigation">
          {visibleItems.map((item) => (
            <Link className={`nav-link ${isActive(pathname, item) ? "active" : ""}`} href={item.href} key={item.label}>
              <Icon name={item.icon} />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          <Link className="nav-link" href="/login">
            <Icon name="help" />
            <span>Help & Support</span>
          </Link>
          <div className="profile">
            <span className="avatar">SG</span>
            <div>
              <strong>{user?.email || "Signed in"}</strong>
              <div className="subtle">{user?.role || "user"}</div>
            </div>
          </div>
        </div>
      </aside>
      <div className="app-main">
        <Topbar />
        <main className="content">{children}</main>
      </div>
    </div>
  );
}

export function Topbar() {
  const router = useRouter();
  const { user } = useAuthToken();
  return (
    <header className="topbar">
      <div className="searchbox">
        <Icon name="search" />
        <span>Search sessions, customers, requirements...</span>
      </div>
      <div className="top-actions">
        <Icon name="bell" />
        <div className="user-pill">
          <span className="avatar" style={{ width: 42, height: 42 }}>
            {(user?.email || "U").slice(0, 2).toUpperCase()}
          </span>
          <strong>{user?.email || "User"}</strong>
          <span className="badge gray">{user?.role || "role"}</span>
        </div>
        <div className="mode-pill">
          <Icon name="data" />
          <span>AI MODE</span>
          <Icon name="chevron" />
        </div>
        <button className="btn ghost" type="button" onClick={() => { clearAuth(); router.replace("/login"); }}>
          Sign out
        </button>
      </div>
    </header>
  );
}
