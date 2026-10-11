"use client";

import { useState } from "react";
import { AppShell } from "../../../components/AppShell";
import { Icon } from "../../../components/Icon";
import { Button } from "../../../components/Primitives";
import { EmptyState, WorkspaceFrame } from "../../../components/Workspace";
import { api } from "../../../lib/api";
import { useAuthToken } from "../../../lib/auth";
import { can } from "../../../lib/rbac";

const rates = [
  ["Solution Architect", 6000],
  ["Product/BA", 4500],
  ["Frontend Engineer", 5000],
  ["Backend Engineer", 5200],
  ["Data/Integration Engineer", 5600],
  ["AI Engineer", 6000],
  ["QA Engineer", 4200],
  ["DevOps Engineer", 5500],
  ["Delivery Manager", 5000],
];

export default function EstimatePage({ params }: { params: { id: string } }) {
  const { token, user } = useAuthToken();
  const [currency, setCurrency] = useState("USD");
  const [contingency, setContingency] = useState(20);
  const [productivity, setProductivity] = useState(1);
  const [capacity, setCapacity] = useState(3);
  const [estimate, setEstimate] = useState<any>(null);
  const [status, setStatus] = useState("");
  const canEstimate = can(user?.role, "estimate");
  const config = {
    currency,
    contingency_pct: contingency / 100,
    productivity_factor: productivity,
    team_capacity_pw_per_week: capacity,
    role_rates: rates.map(([role, rate_per_week]) => ({ role, rate_per_week })),
  };

  async function generate() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/estimate`, { method: "POST", body: JSON.stringify({ config }) }, token);
      setEstimate(result.estimate);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to generate estimate.");
    }
  }

  async function refresh() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/estimate`, {}, token);
      setEstimate(result.estimate || null);
      if (!result.estimate) setStatus("Pending. Generate estimate after scope approval.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to refresh estimate.");
    }
  }

  return (
    <AppShell sessionId={params.id}>
      <WorkspaceFrame
        sessionId={params.id}
        title="Estimation & ROM"
        subtitle="Configure deterministic estimates with visible rules, assumptions and confidence."
        active="estimate"
        actions={
          <div className="filter-row">
            <Button onClick={generate} disabled={!canEstimate}>
              <Icon name="estimate" />
              Generate Estimate
            </Button>
            <Button variant="ghost" onClick={refresh}>
              Refresh
            </Button>
          </div>
        }
      >
        <div className="grid">
          <section className="card pad">
            <div className="form-grid">
              <div className="success-box">Signed in as {user?.email} with {user?.role} access.</div>
              <label className="field">
                <span className="label">Currency</span>
                <input className="input" value={currency} onChange={(event) => setCurrency(event.target.value)} />
              </label>
              <label className="field">
                <span className="label">Contingency %</span>
                <input className="input" type="number" value={contingency} onChange={(event) => setContingency(Number(event.target.value))} />
              </label>
              <label className="field">
                <span className="label">Productivity Factor</span>
                <input className="input" type="number" step="0.1" value={productivity} onChange={(event) => setProductivity(Number(event.target.value))} />
              </label>
              <label className="field">
                <span className="label">Team Capacity PW / Week</span>
                <input className="input" type="number" step="0.5" value={capacity} onChange={(event) => setCapacity(Number(event.target.value))} />
              </label>
            </div>
          </section>

          {status && <div className="alert-box">{status}</div>}
          {!estimate ? (
            <EmptyState title="No estimate yet" text="Generate estimate once the scope is approved." />
          ) : (
            <>
              <div className="grid metrics">
                <div className="card metric-card">
                  <span className="icon-wrap"><Icon name="estimate" /></span>
                  <div>
                    <div className="metric-value">{estimate.total_effort_low_pw}-{estimate.total_effort_high_pw}</div>
                    <div className="metric-label">Person-weeks</div>
                  </div>
                </div>
                <div className="card metric-card">
                  <span className="icon-wrap purple"><Icon name="calendar" /></span>
                  <div>
                    <div className="metric-value">{estimate.timeline_low_weeks}-{estimate.timeline_high_weeks}</div>
                    <div className="metric-label">Timeline weeks</div>
                  </div>
                </div>
                <div className="card metric-card">
                  <span className="icon-wrap success"><Icon name="check" /></span>
                  <div>
                    <div className="metric-value">{estimate.confidence}</div>
                    <div className="metric-label">Confidence</div>
                  </div>
                </div>
                <div className="card metric-card">
                  <span className="icon-wrap warning"><Icon name="alert" /></span>
                  <div>
                    <div className="metric-value">{estimate.config.currency}</div>
                    <div className="metric-label">{Math.round(estimate.rom_low).toLocaleString()}-{Math.round(estimate.rom_high).toLocaleString()}</div>
                  </div>
                </div>
              </div>

              <section className="card pad">
                <div className="card-header">
                  <h2 className="card-title">Workstreams</h2>
                  <span className="badge blue">{estimate.complexity?.complexity_band} complexity</span>
                </div>
                <div className="stack">
                  {(estimate.workstreams || []).map((workstream: any) => (
                    <div className="scenario-card" key={workstream.workstream_id}>
                      <span className="icon-wrap">
                        <Icon name="estimate" />
                      </span>
                      <div>
                        <strong>{workstream.workstream_id} - {workstream.name}</strong>
                        <div className="subtle">{workstream.effort_low_pw}-{workstream.effort_high_pw} PW | {workstream.timeline_low_weeks}-{workstream.timeline_high_weeks} weeks | {workstream.complexity}</div>
                        <p>Drivers: {(workstream.drivers || []).join("; ")}</p>
                        <div className="subtle">Reqs: {(workstream.related_req_ids || []).join(", ") || "-"}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              <section className="card pad">
                <h2 className="card-title">Calculation Rules</h2>
                <ul>
                  {(estimate.calculation_rules || []).map((rule: string) => (
                    <li key={rule}>{rule}</li>
                  ))}
                </ul>
              </section>
            </>
          )}
        </div>
      </WorkspaceFrame>
    </AppShell>
  );
}
