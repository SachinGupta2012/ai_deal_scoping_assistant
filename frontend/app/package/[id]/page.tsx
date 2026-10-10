"use client";
import { useState } from "react";
import { api } from "../../../lib/api";

export default function PackagePage({ params }: { params: { id: string } }) {
  const [token, setToken] = useState("");
  const [changedReqIds, setChangedReqIds] = useState("");
  const [gate, setGate] = useState<any>(null);
  const [impact, setImpact] = useState<any>(null);
  const [pkg, setPkg] = useState<any>(null);
  const [err, setErr] = useState("");
  const impactBody = {
    changed_req_ids: changedReqIds.split(",").map(s => s.trim()).filter(Boolean),
    changed_assumption_ids: [],
    config_changes: {},
  };
  return (<div>
    <h2>Final Package Workspace — {params.id}</h2>
    <input placeholder="paste JWT" value={token} onChange={e => setToken(e.target.value)} style={{ width: "100%" }} />
    <div style={{ display: "flex", gap: 8, margin: "12px 0", flexWrap: "wrap" }}>
      <input placeholder="changed req IDs, e.g. NFR_01, INT_01" value={changedReqIds} onChange={e => setChangedReqIds(e.target.value)} style={{ minWidth: 300 }} />
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/change-impact`, { method: "POST", body: JSON.stringify(impactBody) }, token); setImpact(r.change_impact); } catch (e: any) { setErr(e.message); } }}>Review Change Impact</button>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/quality-gate`, { method: "POST" }, token); setGate(r.quality_gate); } catch (e: any) { setErr(e.message); } }}>Run Quality Gate</button>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/package`, { method: "POST", body: JSON.stringify(impactBody) }, token); setPkg(r.package); setGate(r.package.quality_gate); setImpact(r.package.change_impact); } catch (e: any) { setErr(e.message); } }}>Export Markdown Package</button>
    </div>
    {err && <p>{err}</p>}
    {impact && (<div>
      <h3>Change impact</h3>
      <p><b>Affected outputs:</b> {impact.affected_outputs.join(", ") || "none"}</p>
      <p><b>Affected reqs:</b> {impact.affected_req_ids.join(", ") || "none"} | <b>Unaffected:</b> {impact.unaffected_req_ids.join(", ") || "none"}</p>
      <p><small>Capabilities: {impact.affected_capability_ids.join(", ") || "—"} | Components: {impact.affected_component_ids.join(", ") || "—"} | Workstreams: {impact.affected_workstream_ids.join(", ") || "—"}</small></p>
    </div>)}
    {gate && (<div>
      <h3>Quality gate</h3>
      <p><b>{gate.status}</b> — {gate.summary}</p>
      {gate.issues?.map((i: any) => (<div key={i.issue_id} style={{ border: "1px solid #ddd", padding: 10, margin: "6px 0" }}>
        <b>{i.issue_id}</b> [{i.severity}] {i.category}: {i.message} <small>{i.related_ids.join(", ")}</small>
      </div>))}
    </div>)}
    {pkg && (<div>
      <h3>Package export</h3>
      <p><b>Saved:</b> {pkg.export_path}</p>
      <pre style={{ background: "#f6f6f6", padding: 12, overflowX: "auto", whiteSpace: "pre-wrap" }}>{pkg.markdown}</pre>
    </div>)}
  </div>);
}
