"use client";
import { useState } from "react";
import { api } from "../../../lib/api";

export default function PrdPage({ params }: { params: { id: string } }) {
  const [token, setToken] = useState("");
  const [prd, setPrd] = useState<any>(null);
  const [err, setErr] = useState("");
  return (<div>
    <h2>PRD + Scope Workspace — {params.id}</h2>
    <input placeholder="paste JWT" value={token} onChange={e => setToken(e.target.value)} style={{ width: "100%" }} />
    <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
      <button onClick={async () => { setErr(""); try { await api(`/sessions/${params.id}/prd`, { method: "POST" }, token); setErr("queued — polling…"); } catch (e: any) { setErr(e.message); } }}>Generate PRD (needs approved scope)</button>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/prd`, {}, token); setPrd(r.prd || null); if (!r.prd) setErr("pending — approve scope + generate first"); } catch (e: any) { setErr(e.message); } }}>Refresh</button>
    </div>
    {err && <p>{err}</p>}
    {prd?.coverage && <p><b>Coverage {prd.coverage.coverage_pct}%</b> — uncovered: {prd.coverage.uncovered_req_ids.join(", ") || "none"} {prd.coverage.unsupported_capabilities.length ? `— unsupported: ${prd.coverage.unsupported_capabilities.join(", ")}` : ""}</p>}
    {prd?.capabilities?.map((c: any) => (
      <div key={c.capability_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
        <b>{c.capability_id} — {c.name}</b> [{c.scope_kind}] <i>{c.priority}</i>
        <p>{c.description}</p>
        <small>reqs: {c.included_req_ids.join(", ")}</small>
      </div>))}
  </div>);
}
