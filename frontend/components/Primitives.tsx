import Link from "next/link";
import type { ReactNode } from "react";
import { Icon, type IconName } from "./Icon";
import type { SessionSummary, SessionStatus } from "../lib/catalog";

export function ButtonLink({ href, children, variant = "primary" }: { href: string; children: ReactNode; variant?: "primary" | "ghost" }) {
  return (
    <Link className={`btn ${variant}`} href={href}>
      {children}
    </Link>
  );
}

export function Button({ children, variant = "primary", type = "button", onClick, disabled }: { children: ReactNode; variant?: "primary" | "ghost" | "danger"; type?: "button" | "submit"; onClick?: () => void; disabled?: boolean }) {
  return (
    <button className={`btn ${variant}`} type={type} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export function MetricCard({ label, value, trend, tone, icon }: { label: string; value: string; trend: string; tone: string; icon: IconName }) {
  const trendClass = trend.startsWith("+") ? (tone === "danger" ? "bad" : "up") : "";
  return (
    <div className="card metric-card">
      <span className={`icon-wrap ${tone}`}>
        <Icon name={icon} />
      </span>
      <div>
        <div className="metric-value">{value}</div>
        <div className="metric-label">{label}</div>
      </div>
      <div className={`metric-trend ${trendClass}`}>{trend}</div>
    </div>
  );
}

export function StatusBadge({ status }: { status: SessionStatus | string }) {
  const tone = status === "Completed" ? "green" : status === "Needs Review" ? "red" : status === "Not Started" ? "gray" : "blue";
  return <span className={`badge ${tone}`}>{status}</span>;
}

export function ProgressBar({ value, complete }: { value: number; complete?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div className={`progress ${complete ? "green" : ""}`}>
        <span style={{ width: `${Math.max(0, Math.min(100, value))}%` }} />
      </div>
      <span className="subtle">{value}%</span>
    </div>
  );
}

export function SessionTable({ sessions, compact = false }: { sessions: SessionSummary[]; compact?: boolean }) {
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead>
          <tr>
            {!compact && <th>#</th>}
            <th>Session Name</th>
            <th>Customer / Opportunity</th>
            {!compact && <th>Engagement Type</th>}
            <th>Status</th>
            <th>Progress</th>
            <th>Last Updated</th>
            {!compact && <th>Owner</th>}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((session) => (
            <tr key={session.id}>
              {!compact && <td>{session.id}</td>}
              <td>
                <Link className="link-text" href={`/requirements/${session.id}`}>
                  {session.name}
                </Link>
                <div className="subtle">{session.subtitle}</div>
              </td>
              <td>
                {session.customer}
                <div className="subtle">{session.opportunity}</div>
              </td>
              {!compact && <td>{session.engagementType}</td>}
              <td>
                <StatusBadge status={session.status} />
              </td>
              <td>
                <ProgressBar value={session.progress} complete={session.status === "Completed"} />
              </td>
              <td>{session.updated}</td>
              {!compact && (
                <td>
                  <div className="profile">
                    <span className="avatar" style={{ width: 32, height: 32, fontSize: 12 }}>
                      {session.ownerInitials}
                    </span>
                    <span>{session.owner}</span>
                  </div>
                </td>
              )}
              <td>
                <Link className="link-text" href={`/requirements/${session.id}`}>
                  <Icon name="chevron" />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function WorkflowStepper({ active = 1 }: { active?: number }) {
  const items = ["Requirements", "PRD & Scope", "Solution Design", "Data & AI", "Estimation", "Validation", "Export"];
  const descriptions = ["Upload & analyze", "Generate PRD", "Cloud architecture", "Data and AI strategy", "Timeline and ROM", "Quality checks", "Final package"];
  return (
    <div className="workflow">
      {items.map((item, index) => (
        <div className={`step ${index + 1 === active ? "active" : ""}`} key={item}>
          <div className="step-number">{index + 1}</div>
          <div className="step-label">{item}</div>
          <div className="subtle">{descriptions[index]}</div>
        </div>
      ))}
    </div>
  );
}
