"use client";

import { useEffect, useMemo, useState } from "react";
import { Icon } from "./Icon";
import { MetricCard, SessionTable } from "./Primitives";
import { EmptyState } from "./Workspace";
import { api } from "../lib/api";
import { useAuthToken } from "../lib/auth";
import type { SessionSummary, SessionStatus } from "../lib/catalog";
import { sessionMetrics } from "./DashboardClient";

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
    owner: "Sachin Gupta",
    ownerInitials: "SG",
  };
}

export function SessionsClient() {
  const { token, user } = useAuthToken();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [status, setStatus] = useState("");

  async function loadSessions() {
    if (!token) return;
    try {
      const result = await api("/sessions", {}, token);
      const rows = (result.sessions || []).map(mapSession);
      setSessions(rows);
      setStatus(rows.length ? "" : "No live sessions yet. Create a session to populate this page.");
    } catch (error) {
      setSessions([]);
      setStatus(error instanceof Error ? error.message : "Failed to load sessions.");
    }
  }

  useEffect(() => {
    loadSessions();
  }, [token]);

  const liveMetrics = useMemo(() => sessionMetrics(sessions), [sessions]);

  return (
    <div className="grid">
      <div className="grid metrics">
        {liveMetrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </div>

      <section className="card pad">
        <div className="filter-row" style={{ marginBottom: 16 }}>
          <span className="badge blue">Signed in: {user?.email}</span>
          <div className="searchbox" style={{ width: 340 }}>
            <Icon name="search" />
            <span>Search by session name, customer, or opportunity...</span>
          </div>
          <select className="select" style={{ width: 140 }} defaultValue="all">
            <option value="all">All Statuses</option>
            <option>In Progress</option>
            <option>Completed</option>
            <option>Needs Review</option>
          </select>
          <button className="btn ghost" type="button" onClick={loadSessions}>
            <Icon name="filter" />
            Refresh
          </button>
        </div>
        {status && <div className="alert-box" style={{ marginBottom: 14 }}>{status}</div>}
        {sessions.length ? <SessionTable sessions={sessions} /> : <EmptyState title="No sessions in the database" text="Create a scoping session to show real backend data here." />}
        <div className="card-header" style={{ marginTop: 18, marginBottom: 0 }}>
          <span className="subtle">Showing {Math.min(1, sessions.length)} to {sessions.length} of {sessions.length} sessions</span>
          <select className="select" style={{ width: 130 }} defaultValue="10">
            <option value="10">10 per page</option>
            <option value="25">25 per page</option>
          </select>
        </div>
      </section>
    </div>
  );
}
