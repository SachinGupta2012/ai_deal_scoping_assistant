"use client";
import { useState } from "react";
import { api } from "../../../lib/api";
import { MermaidPreview } from "../../../lib/MermaidPreview";

export default function ArchPage({ params }: { params: { id: string } }) {
  const [token, setToken] = useState("");
  const [platform, setPlatform] = useState("auto");
  const [arch, setArch] = useState<any>(null);
  const [err, setErr] = useState("");
  return (<div>
    <h2>Architecture Workspace — {params.id}</h2>
    <input placeholder="paste JWT" value={token} onChange={e => setToken(e.target.value)} style={{ width: "100%" }} />
    <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
      <select value={platform} onChange={e => setPlatform(e.target.value)}>
        <option value="auto">Auto-recommend</option>
        <option value="aws">AWS</option>
        <option value="azure">Azure</option>
        <option value="gcp">GCP</option>
      </select>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/architecture`, { method: "POST", body: JSON.stringify({ platform }) }, token); setErr(`queued — platform: ${r.platform}`); } catch (e: any) { setErr(e.message); } }}>Generate Architecture</button>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/architecture`, {}, token); setArch(r.architecture || null); if (!r.architecture) setErr("pending — approve scope + generate first"); } catch (e: any) { setErr(e.message); } }}>Refresh</button>
    </div>
    {err && <p>{err}</p>}
    {arch && (<div>
      <p><b>Platform: {arch.platform}</b> — {arch.platform_rationale}</p>
      {arch.validation?.off_catalog?.length ? <p style={{ color: "red" }}>Off-catalog: {arch.validation.off_catalog.join(", ")}</p> : null}
      {arch.validation?.missing_layers?.length ? <p style={{ color: "red" }}>Missing layers: {arch.validation.missing_layers.join(", ")}</p> : null}
      <MermaidPreview source={arch.mermaid} />
      <pre style={{ background: "#f6f6f6", padding: 12, overflowX: "auto" }}>{arch.mermaid}</pre>
      {arch.components?.map((c: any) => (
        <div key={c.component_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
          <b>{c.component_id} — {c.name}</b> [{c.layer}] <i>{c.cloud_service}</i>
          <p>{c.purpose}</p>
          <small>Rationale: {c.rationale} | Tradeoffs: {c.tradeoffs || "—"} | Reqs: {c.supported_req_ids.join(", ")} | Sec: {c.security || "—"}</small>
        </div>))}
    </div>)}
  </div>);
}
