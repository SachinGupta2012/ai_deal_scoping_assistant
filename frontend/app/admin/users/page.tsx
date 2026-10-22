"use client";

import { useEffect, useState } from "react";
import { AppShell } from "../../../components/AppShell";
import { Icon } from "../../../components/Icon";
import { Button } from "../../../components/Primitives";
import { api } from "../../../lib/api";
import { useAuthToken, type UserRole } from "../../../lib/auth";
import { can, roleDescriptions } from "../../../lib/rbac";

type UserRow = {
  id: string;
  email: string;
  role: UserRole;
};

const roles: UserRole[] = ["admin", "sales", "architect", "ba", "delivery", "reviewer", "viewer"];

export default function UsersPage() {
  const { token, user } = useAuthToken();
  const [users, setUsers] = useState<UserRow[]>([]);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("sales");
  const [status, setStatus] = useState("");
  const allowed = can(user?.role, "manageUsers");

  async function loadUsers() {
    if (!token || !allowed) return;
    try {
      const result = await api("/auth/users", {}, token);
      setUsers(result.users || []);
      setStatus("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to load users.");
    }
  }

  async function createUser() {
    setStatus("");
    try {
      await api("/auth/users", { method: "POST", body: JSON.stringify({ email, password, role }) }, token);
      setEmail("");
      setPassword("");
      await loadUsers();
      setStatus("User created.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to create user.");
    }
  }

  useEffect(() => {
    loadUsers();
  }, [token, allowed]);

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">User Management</h1>
          <div className="eyebrow">Create role-based users for the scoping workflow.</div>
        </div>
      </div>

      {!allowed ? (
        <div className="alert-box">Only admins can manage users.</div>
      ) : (
        <div className="grid">
          <section className="card pad">
            <div className="form-grid">
              <label className="field">
                <span className="label">Email</span>
                <input className="input" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="user@company.com" />
              </label>
              <label className="field">
                <span className="label">Temporary Password</span>
                <input className="input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Minimum 8 characters" />
              </label>
              <label className="field">
                <span className="label">Role</span>
                <select className="select" value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
                  {roles.map((item) => (
                    <option key={item}>{item}</option>
                  ))}
                </select>
              </label>
              <div className="field">
                <span className="label">Access</span>
                <div className="subtle">{roleDescriptions[role]}</div>
              </div>
            </div>
            <div className="filter-row" style={{ marginTop: 16 }}>
              <Button onClick={createUser}>
                <Icon name="plus" />
                Create User
              </Button>
              <Button variant="ghost" onClick={loadUsers}>
                Refresh
              </Button>
            </div>
          </section>

          {status && <div className={status === "User created." ? "success-box" : "alert-box"}>{status}</div>}

          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Users</h2>
              <span className="subtle">{users.length} users</span>
            </div>
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Access Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((row) => (
                    <tr key={row.id}>
                      <td>{row.email}</td>
                      <td><span className="badge blue">{row.role}</span></td>
                      <td>{roleDescriptions[row.role]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}
    </AppShell>
  );
}
