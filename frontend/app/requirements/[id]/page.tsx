"use client";

import { useEffect, useMemo, useState } from "react";
import { AppShell } from "../../../components/AppShell";
import { Icon } from "../../../components/Icon";
import { Button } from "../../../components/Primitives";
import { EmptyState, WorkspaceFrame } from "../../../components/Workspace";
import { api } from "../../../lib/api";
import { useAuthToken } from "../../../lib/auth";
import { can } from "../../../lib/rbac";

type Requirement = {
  req_id: string;
  type: string;
  description: string;
  priority: string;
  chunk_id: string;
  quote: string;
  origin: string;
  questions?: string[];
};

type ScopeResponse = {
  version_no?: number;
  status?: string;
  scope?: {
    requirements?: Requirement[];
    assumptions?: { asm_id: string; text: string; needs_review?: boolean }[];
    questions?: { q_id: string; text: string; blocking?: boolean }[];
  };
};

export default function ReqPage({ params }: { params: { id: string } }) {
  const { token, user } = useAuthToken();
  const [scope, setScope] = useState<ScopeResponse | null>(null);
  const [typeFilter, setTypeFilter] = useState("all");
  const [originFilter, setOriginFilter] = useState("all");
  const [editing, setEditing] = useState<Requirement | null>(null);
  const [editDescription, setEditDescription] = useState("");
  const [status, setStatus] = useState("");

  async function refresh() {
    if (!token) return;
    try {
      const result = await api(`/sessions/${params.id}/scope`, {}, token);
      setScope(result);
      if (!result.scope) setStatus("Waiting for scope analysis.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to load scope.");
    }
  }

  useEffect(() => {
    refresh();
  }, [token, params.id]);

  const requirements = scope?.scope?.requirements || [];
  const filtered = useMemo(
    () => requirements.filter((req) => (typeFilter === "all" || req.type === typeFilter) && (originFilter === "all" || req.origin === originFilter)),
    [requirements, typeFilter, originFilter],
  );
  const types = Array.from(new Set(requirements.map((req) => req.type)));
  const origins = Array.from(new Set(requirements.map((req) => req.origin)));
  const canAnalyze = can(user?.role, "ingestAnalyze");
  const canApprove = can(user?.role, "approveScope");
  const canEdit = can(user?.role, "editScope");

  async function analyze() {
    setStatus("");
    try {
      await api(`/sessions/${params.id}/analyze`, { method: "POST" }, token);
      setStatus("Analysis queued. Refresh in a few seconds.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to queue analysis.");
    }
  }

  async function approve() {
    setStatus("");
    try {
      await api(`/sessions/${params.id}/approve`, { method: "POST" }, token);
      await refresh();
      setStatus("Scope approved. You can generate PRD next.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to approve scope.");
    }
  }

  async function saveEdit() {
    if (!editing) return;
    setStatus("");
    try {
      await api(`/sessions/${params.id}/scope/items`, { method: "PATCH", body: JSON.stringify({ req_id: editing.req_id, description: editDescription }) }, token);
      setEditing(null);
      await refresh();
      setStatus("Requirement updated as a new scope version.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to update requirement.");
    }
  }

  return (
    <AppShell sessionId={params.id}>
      <WorkspaceFrame
        sessionId={params.id}
        title="Requirements Workspace"
        subtitle="Review extracted requirements, source evidence, assumptions and clarification gaps."
        active="requirements"
        actions={
          <div className="filter-row">
            <Button onClick={analyze} disabled={!canAnalyze}>
              <Icon name="spark" />
              Analyze
            </Button>
            <Button variant="ghost" onClick={refresh}>
              Refresh
            </Button>
            <Button variant="ghost" onClick={approve} disabled={!canApprove}>
              <Icon name="check" />
              Approve Scope
            </Button>
          </div>
        }
      >
        <div className="grid">
          <section className="card pad">
            <div className="filter-row">
              <span className="badge blue">Signed in: {user?.email}</span>
              <select className="select" value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} style={{ width: 160 }}>
                <option value="all">All Types</option>
                {types.map((type) => (
                  <option key={type}>{type}</option>
                ))}
              </select>
              <select className="select" value={originFilter} onChange={(event) => setOriginFilter(event.target.value)} style={{ width: 190 }}>
                <option value="all">All Origins</option>
                {origins.map((origin) => (
                  <option key={origin}>{origin}</option>
                ))}
              </select>
              <span className="badge blue">v{scope?.version_no || "-"}</span>
              <span className={`badge ${scope?.status === "approved" ? "green" : "gray"}`}>{scope?.status || "pending"}</span>
            </div>
          </section>

          {status && <div className={status.includes("approved") || status.includes("updated") ? "success-box" : "alert-box"}>{status}</div>}

          {!requirements.length ? (
            <EmptyState title="No requirements yet" text="Create a session, ingest requirements, then run analysis." />
          ) : (
            <section className="card pad">
              <div className="card-header">
                <h2 className="card-title">Extracted Requirements</h2>
                <span className="subtle">{filtered.length} of {requirements.length} shown</span>
              </div>
              <div className="table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Type</th>
                      <th>Requirement</th>
                      <th>Priority</th>
                      <th>Origin</th>
                      <th>Source</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((req) => (
                      <tr key={req.req_id}>
                        <td><strong>{req.req_id}</strong></td>
                        <td><span className="badge blue">{req.type}</span></td>
                        <td style={{ whiteSpace: "normal", minWidth: 380 }}>{req.description}</td>
                        <td>{req.priority}</td>
                        <td>{req.origin}</td>
                        <td style={{ whiteSpace: "normal", maxWidth: 280 }}>
                          <div className="subtle">Chunk {req.chunk_id}</div>
                          <div>{req.quote?.slice(0, 150)}</div>
                        </td>
                        <td>
                          <button
                            className="btn ghost"
                            type="button"
                            disabled={!canEdit}
                            onClick={() => {
                              setEditing(req);
                              setEditDescription(req.description);
                            }}
                          >
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          <div className="split">
            <section className="card pad">
              <h2 className="card-title">Assumptions</h2>
              <div className="stack" style={{ marginTop: 16 }}>
                {(scope?.scope?.assumptions || []).map((assumption) => (
                  <div className="attention-item" key={assumption.asm_id}>
                    <span>{assumption.text}</span>
                    <span className={`badge ${assumption.needs_review ? "red" : "green"}`}>{assumption.needs_review ? "Review" : "Accepted"}</span>
                  </div>
                ))}
              </div>
            </section>
            <section className="card pad">
              <h2 className="card-title">Clarification Questions</h2>
              <div className="stack" style={{ marginTop: 16 }}>
                {(scope?.scope?.questions || []).map((question) => (
                  <div className="attention-item" key={question.q_id}>
                    <span>{question.text}</span>
                    <span className={`badge ${question.blocking ? "red" : "gray"}`}>{question.blocking ? "Blocking" : "Open"}</span>
                  </div>
                ))}
              </div>
            </section>
          </div>
        </div>

        {editing && (
          <div className="card pad" style={{ marginTop: 18 }}>
            <div className="card-header">
              <h2 className="card-title">Edit {editing.req_id}</h2>
              <button className="btn" type="button" onClick={() => setEditing(null)}>
                Cancel
              </button>
            </div>
            <textarea className="textarea" value={editDescription} onChange={(event) => setEditDescription(event.target.value)} />
            <div className="filter-row" style={{ marginTop: 14 }}>
              <Button onClick={saveEdit}>Save New Version</Button>
            </div>
          </div>
        )}
      </WorkspaceFrame>
    </AppShell>
  );
}
