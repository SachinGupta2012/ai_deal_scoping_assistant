"use client";
import { useState } from "react";
import { api } from "../../../lib/api";

export default function PrdPage({ params }: { params: { id: string } }) {
  const [token, setToken] = useState("");
  const [prd, setPrd] = useState<any>(null);
  const [scope, setScope] = useState<any>(null);
  const [err, setErr] = useState("");
  return (<div>
    <h2>PRD + Scope Workspace — {params.id}</h2>
    <input placeholder="paste JWT" value={token} onChange={e => setToken(e.target.value)} style={{ width: "100%" }} />
    <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
      <button onClick={async () => { setErr(""); try { await api(`/sessions/${params.id}/prd`, { method: "POST" }, token); setErr("queued — polling…"); } catch (e: any) { setErr(e.message); } }}>Generate PRD (needs approved scope)</button>
      <button onClick={async () => { setErr(""); try { const [r, s] = await Promise.all([api(`/sessions/${params.id}/prd`, {}, token), api(`/sessions/${params.id}/scope`, {}, token)]); setPrd(r.prd || null); setScope(s.scope || null); if (!r.prd) setErr("pending — approve scope + generate first"); } catch (e: any) { setErr(e.message); } }}>Refresh</button>
    </div>
    {err && <p>{err}</p>}
    {prd?.coverage && <p><b>Coverage {prd.coverage.coverage_pct}%</b> — uncovered: {prd.coverage.uncovered_req_ids.join(", ") || "none"} {prd.coverage.unsupported_capabilities.length ? `— unsupported: ${prd.coverage.unsupported_capabilities.join(", ")}` : ""}</p>}
    {prd?.capabilities && scope?.requirements && (<div>
      <h3>Coverage matrix</h3>
      <table style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead><tr><th style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>Requirement</th>{prd.capabilities.map((c: any) => <th key={c.capability_id} style={{ borderBottom: "1px solid #ddd" }}>{c.capability_id}</th>)}</tr></thead>
        <tbody>{scope.requirements.map((r: any) => <tr key={r.req_id}>
          <td style={{ borderBottom: "1px solid #eee", padding: 6 }}>{r.req_id}</td>
          {prd.capabilities.map((c: any) => <td key={c.capability_id} style={{ textAlign: "center", borderBottom: "1px solid #eee", padding: 6 }}>{c.included_req_ids.includes(r.req_id) ? "yes" : ""}</td>)}
        </tr>)}</tbody>
      </table>
    </div>)}
    {prd?.capabilities?.map((c: any) => (
      <div key={c.capability_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
        <b>{c.capability_id} — {c.name}</b> [{c.scope_kind}] <i>{c.priority}</i>
        <p>{c.description}</p>
        <small>reqs: {c.included_req_ids.join(", ")}</small>
      </div>))}
  </div>);
}
