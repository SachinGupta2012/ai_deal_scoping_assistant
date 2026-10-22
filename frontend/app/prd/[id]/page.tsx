"use client";

import { useState } from "react";
import { AppShell } from "../../../components/AppShell";
import { Icon } from "../../../components/Icon";
import { Button } from "../../../components/Primitives";
import { EmptyState, WorkspaceFrame } from "../../../components/Workspace";
import { api } from "../../../lib/api";
import { useAuthToken } from "../../../lib/auth";
import { can } from "../../../lib/rbac";

type Capability = {
  capability_id: string;
  name: string;
  description: string;
  priority: string;
  scope_kind: string;
  included_req_ids: string[];
};

export default function PrdPage({ params }: { params: { id: string } }) {
  const { token, user } = useAuthToken();
  const [prd, setPrd] = useState<any>(null);
  const [scope, setScope] = useState<any>(null);
  const [status, setStatus] = useState("");
  const canGenerate = can(user?.role, "generatePrd");

  async function refresh() {
    setStatus("");
    try {
      const [prdResult, scopeResult] = await Promise.all([api(`/sessions/${params.id}/prd`, {}, token), api(`/sessions/${params.id}/scope`, {}, token)]);
      setPrd(prdResult.prd || null);
      setScope(scopeResult.scope || null);
      if (!prdResult.prd) setStatus("Pending. Approve scope, then generate PRD.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to refresh PRD.");
    }
  }

  async function generate() {
    setStatus("");
    try {
      await api(`/sessions/${params.id}/prd`, { method: "POST" }, token);
      setStatus("PRD generation queued. Refresh in a few seconds.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to generate PRD.");
    }
  }

  return (
    <AppShell sessionId={params.id}>
      <WorkspaceFrame
        sessionId={params.id}
        title="PRD & Functional Scope"
        subtitle="Generate customer-ready scope, capabilities, journeys and traceability."
        active="prd"
        actions={
          <div className="filter-row">
            <Button onClick={generate} disabled={!canGenerate}>
              <Icon name="spark" />
              Generate PRD
            </Button>
            <Button variant="ghost" onClick={refresh}>
              Refresh
            </Button>
          </div>
        }
      >
        <div className="grid">
          <section className="card pad">
            <div className="filter-row">
              <span className="badge blue">Signed in: {user?.email}</span>
              {prd?.coverage && <span className="badge green">Coverage {prd.coverage.coverage_pct}%</span>}
            </div>
          </section>

          {status && <div className="alert-box">{status}</div>}
          {!prd ? (
            <EmptyState title="No PRD generated yet" text="Generate PRD after approving the requirements scope." />
          ) : (
            <>
              <section className="card pad">
                <div className="card-header">
                  <h2 className="card-title">Coverage Matrix</h2>
                  <span className="subtle">Uncovered: {prd.coverage?.uncovered_req_ids?.join(", ") || "none"}</span>
                </div>
                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Requirement</th>
                        {(prd.capabilities || []).map((capability: Capability) => (
                          <th key={capability.capability_id}>{capability.capability_id}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(scope?.requirements || []).map((req: { req_id: string }) => (
                        <tr key={req.req_id}>
                          <td>{req.req_id}</td>
                          {(prd.capabilities || []).map((capability: Capability) => (
                            <td key={capability.capability_id}>{capability.included_req_ids.includes(req.req_id) ? "yes" : ""}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              <section className="card pad">
                <div className="card-header">
                  <h2 className="card-title">Capabilities</h2>
                  <span className="subtle">{prd.capabilities?.length || 0} generated</span>
                </div>
                <div className="stack">
                  {(prd.capabilities || []).map((capability: Capability) => (
                    <div className="scenario-card" key={capability.capability_id}>
                      <span className="icon-wrap">
                        <Icon name="prd" />
                      </span>
                      <div>
                        <strong>{capability.capability_id} - {capability.name}</strong>
                        <div className="subtle">{capability.scope_kind} | {capability.priority} | Reqs: {capability.included_req_ids.join(", ")}</div>
                        <p>{capability.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </div>
      </WorkspaceFrame>
    </AppShell>
  );
}
