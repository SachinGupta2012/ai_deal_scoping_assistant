"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Icon } from "./Icon";
import { ButtonLink, MetricCard, SessionTable, WorkflowStepper } from "./Primitives";
import { EmptyState } from "./Workspace";
import { api } from "../lib/api";
import { useAuthToken } from "../lib/auth";
import { can } from "../lib/rbac";
import type { SessionSummary, SessionStatus } from "../lib/catalog";

type ApiSession = {
  id: string;
  title: string;
  status: string;
  created_at?: string | null;
  opportunity_context?: {
    customer?: string;
    engagement_type?: string;
    description?: string;
  };
};

function mapStatus(status: string): SessionStatus {
  if (status === "approved" || status === "completed") return "Completed";
  if (status === "review" || status === "needs_review") return "Needs Review";
  if (status === "draft") return "In Progress";
  return "Not Started";
}

function mapSession(session: ApiSession, index: number): SessionSummary {
  const mappedStatus = mapStatus(session.status);
  return {
    id: session.id,
    name: session.title,
    subtitle: session.opportunity_context?.description || "Customer scoping session",
    customer: session.opportunity_context?.customer || "Unassigned",
    opportunity: `OPP-${String(index + 1).padStart(4, "0")}`,
    engagementType: session.opportunity_context?.engagement_type || "RFP",
    status: mappedStatus,
    progress: mappedStatus === "Completed" ? 100 : mappedStatus === "Needs Review" ? 40 : mappedStatus === "In Progress" ? 60 : 0,
    updated: session.created_at ? new Date(session.created_at).toLocaleString() : "-",
    owner: "Current user",
    ownerInitials: "CU",
  };
}

export function useLiveSessions() {
  const { token } = useAuthToken();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [status, setStatus] = useState("");

  async function loadSessions() {
    if (!token) return;
    try {
      const result = await api("/sessions", {}, token);
      setSessions((result.sessions || []).map(mapSession));
      setStatus("");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to load sessions.");
    }
  }

  useEffect(() => {
    loadSessions();
  }, [token]);

  return { sessions, status, loadSessions };
}

export function sessionMetrics(sessions: SessionSummary[]) {
  return [
    { label: "Total Sessions", value: String(sessions.length), trend: "Live database", tone: "blue", icon: "document" as const },
    { label: "In Progress", value: String(sessions.filter((session) => session.status === "In Progress").length), trend: "Active work", tone: "blue", icon: "clock" as const },
    { label: "Completed", value: String(sessions.filter((session) => session.status === "Completed").length), trend: "Ready packages", tone: "success", icon: "check" as const },
    { label: "Needs Review", value: String(sessions.filter((session) => session.status === "Needs Review").length), trend: "Requires attention", tone: "danger", icon: "alert" as const },
  ];
}

export function DashboardClient() {
  const { user } = useAuthToken();
  const { sessions, status } = useLiveSessions();
  const metrics = useMemo(() => sessionMetrics(sessions), [sessions]);
  const canCreate = can(user?.role, "createSession");

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Good morning</h1>
          <div className="eyebrow">Turn customer inputs into structured, reviewable and traceable solution scopes.</div>
        </div>
        {canCreate && (
          <ButtonLink href="/sessions/new">
            <Icon name="plus" />
            New Scoping Session
          </ButtonLink>
        )}
      </div>

      <div className="dashboard-layout">
        <div className="grid">
          <div className="grid metrics">
            {metrics.map((metric) => (
              <MetricCard key={metric.label} {...metric} />
            ))}
          </div>

          {status && <div className="alert-box">{status}</div>}

          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Recent Scoping Sessions</h2>
              <Link className="link-text" href="/sessions">
                View All
              </Link>
            </div>
            {sessions.length ? <SessionTable sessions={sessions.slice(0, 5)} compact /> : <EmptyState title="No sessions yet" text="Create your first scoping session to populate this dashboard from the database." />}
          </section>

          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Scoping Workflow</h2>
              <Link className="link-text" href="/sessions">
                Go to Sessions
              </Link>
            </div>
            <WorkflowStepper active={1} />
          </section>
        </div>

        <aside className="grid">
          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">AI Assistant Ready</h2>
              <span className="badge green">Ready</span>
            </div>
            <p className="eyebrow">Analyze requirements, generate insights and create structured deliverables.</p>
            {canCreate ? (
              <ButtonLink href="/sessions/new">
                <Icon name="spark" />
                Analyze New Requirements
              </ButtonLink>
            ) : (
              <div className="alert-box">Your role has read-only or review access. Ask an admin for session creation access.</div>
            )}
          </section>

          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Open Items Requiring Attention</h2>
              <Link className="link-text" href="/sessions">
                View All
              </Link>
            </div>
            <div className="stack">
              {[
                ["Unanswered Questions", "0", "help"],
                ["Uncovered Requirements", "0", "document"],
                ["Inconsistent Assumptions", "0", "alert"],
                ["Validation Issues", "0", "shield"],
              ].map(([label, count, icon]) => (
                <div className="attention-item" key={label}>
                  <span style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span className="icon-wrap">
                      <Icon name={icon as "help"} />
                    </span>
                    <strong>{label}</strong>
                  </span>
                  <span className="badge gray">{count}</span>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </>
  );
}
