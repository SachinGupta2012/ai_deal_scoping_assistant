"use client";
import { useState } from "react";
import { api } from "../../../lib/api";

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
  const [token, setToken] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [contingency, setContingency] = useState(20);
  const [productivity, setProductivity] = useState(1);
  const [capacity, setCapacity] = useState(3);
  const [estimate, setEstimate] = useState<any>(null);
  const [err, setErr] = useState("");
  const config = {
    currency,
    contingency_pct: contingency / 100,
    productivity_factor: productivity,
    team_capacity_pw_per_week: capacity,
    role_rates: rates.map(([role, rate_per_week]) => ({ role, rate_per_week })),
  };
  return (<div>
    <h2>Estimate Workspace — {params.id}</h2>
    <input placeholder="paste JWT" value={token} onChange={e => setToken(e.target.value)} style={{ width: "100%" }} />
    <div style={{ display: "flex", gap: 8, margin: "12px 0", flexWrap: "wrap" }}>
      <label>Currency <input value={currency} onChange={e => setCurrency(e.target.value)} style={{ width: 80 }} /></label>
      <label>Contingency % <input type="number" value={contingency} onChange={e => setContingency(Number(e.target.value))} style={{ width: 80 }} /></label>
      <label>Productivity <input type="number" step="0.1" value={productivity} onChange={e => setProductivity(Number(e.target.value))} style={{ width: 80 }} /></label>
      <label>Team capacity PW/week <input type="number" step="0.5" value={capacity} onChange={e => setCapacity(Number(e.target.value))} style={{ width: 80 }} /></label>
    </div>
    <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/estimate`, { method: "POST", body: JSON.stringify({ config }) }, token); setEstimate(r.estimate); } catch (e: any) { setErr(e.message); } }}>Generate Estimate</button>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/estimate`, {}, token); setEstimate(r.estimate || null); if (!r.estimate) setErr("pending — approve scope + generate first"); } catch (e: any) { setErr(e.message); } }}>Refresh</button>
    </div>
    {err && <p>{err}</p>}
    {estimate && (<div>
      <p><b>Effort:</b> {estimate.total_effort_low_pw}-{estimate.total_effort_high_pw} person-weeks | <b>Timeline:</b> {estimate.timeline_low_weeks}-{estimate.timeline_high_weeks} weeks | <b>ROM:</b> {estimate.config.currency} {Math.round(estimate.rom_low).toLocaleString()}-{Math.round(estimate.rom_high).toLocaleString()} | <b>Confidence:</b> {estimate.confidence}</p>
      <p><b>Complexity:</b> {estimate.complexity.complexity_band} score {estimate.complexity.complexity_score} — capabilities {estimate.complexity.capability_count}, integrations {estimate.complexity.integration_count}, data {estimate.complexity.data_domain_count}, AI {estimate.complexity.ai_use_case_count}</p>
      {estimate.missing_inputs?.length ? <p style={{ color: "#a15c00" }}><b>Missing inputs:</b> {estimate.missing_inputs.join("; ")}</p> : null}
      <h3>Workstreams</h3>
      {estimate.workstreams?.map((w: any) => (<div key={w.workstream_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
        <b>{w.workstream_id} — {w.name}</b> [{w.complexity}] <small>{w.effort_low_pw}-{w.effort_high_pw} PW | {w.timeline_low_weeks}-{w.timeline_high_weeks} weeks | rate {estimate.config.currency} {Math.round(w.blended_rate_per_week).toLocaleString()}/PW</small>
        <p><small>Reqs: {w.related_req_ids.join(", ") || "—"} | Drivers: {w.drivers.join("; ")}</small></p>
      </div>))}
      <h3>Rules</h3>
      <ul>{estimate.calculation_rules?.map((r: string) => <li key={r}>{r}</li>)}</ul>
    </div>)}
  </div>);
}
