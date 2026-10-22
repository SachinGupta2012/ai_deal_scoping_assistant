"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Brand } from "../../components/Brand";
import { Icon, type IconName } from "../../components/Icon";
import { Button } from "../../components/Primitives";
import { api } from "../../lib/api";
import { setStoredToken, setStoredUser } from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function login() {
    setBusy(true);
    setError("");
    try {
      const result = await api("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
      setStoredToken(result.access_token);
      setStoredUser({ email: result.user.email, role: result.user.role });
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <section className="login-hero">
        <Brand />
        <h1>
          Turn customer requirements into clear, structured <span className="accent">solution scopes.</span>
        </h1>
        <p className="eyebrow" style={{ color: "#cbd7ea", maxWidth: 760 }}>
          An intelligent workspace for Sales, Solution Architects, Delivery Managers and Product teams to analyze requirements, design solutions and create complete scoping packages.
        </p>
        <div className="login-features">
          {[
            ["document", "Extract & structure requirements"],
            ["prd", "Generate PRD & functional scope"],
            ["design", "Design cloud architecture"],
            ["data", "Data, integration & AI strategy"],
            ["estimate", "Effort estimation & ROM commercials"],
            ["change", "Validation & export ready package"],
          ].map(([icon, text]) => (
            <div className="feature-row" key={text}>
              <span className="icon-wrap purple">
                <Icon name={icon as IconName} />
              </span>
              <span>{text}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="login-panel-wrap">
        <div className="card login-card">
          <h1>Welcome back</h1>
          <p className="eyebrow">Sign in to access your scoping sessions and continue building great solutions.</p>
          <div className="stack" style={{ marginTop: 14 }}>
            <label className="field" style={{ textAlign: "left" }}>
              <span className="label">Email address</span>
              <input className="input" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" />
            </label>
            <label className="field" style={{ textAlign: "left" }}>
              <span className="label">Password</span>
              <input className="input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter your password" />
            </label>
            {error && <div className="alert-box">{error}</div>}
            <Button onClick={login} disabled={busy}>
              {busy ? "Signing in..." : "Sign in"}
              <Icon name="arrow" />
            </Button>
          </div>
          <p className="eyebrow">Need an account? Ask an admin to create a role-based user.</p>
        </div>
      </section>
    </div>
  );
}
