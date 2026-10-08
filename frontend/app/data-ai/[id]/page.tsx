"use client";
import { useState } from "react";
import { api } from "../../../lib/api";

export default function DataAiPage({ params }: { params: { id: string } }) {
  const [token, setToken] = useState("");
  const [data, setData] = useState<any>(null);
  const [err, setErr] = useState("");
  return (<div>
    <h2>Data, Integration & AI Workspace — {params.id}</h2>
    <input placeholder="paste JWT" value={token} onChange={e => setToken(e.target.value)} style={{ width: "100%" }} />
    <div style={{ display: "flex", gap: 8, margin: "12px 0" }}>
      <button onClick={async () => { setErr(""); try { await api(`/sessions/${params.id}/data-ai`, { method: "POST" }, token); setErr("queued — polling…"); } catch (e: any) { setErr(e.message); } }}>Generate Strategy</button>
      <button onClick={async () => { setErr(""); try { const r = await api(`/sessions/${params.id}/data-ai`, {}, token); setData(r.data_ai || null); if (!r.data_ai) setErr("pending — approve scope + generate first"); } catch (e: any) { setErr(e.message); } }}>Refresh</button>
    </div>
    {err && <p>{err}</p>}
    {data && (<div>
      {data.coverage && <p><b>Coverage {data.coverage.coverage_pct}%</b> — uncovered: {data.coverage.uncovered_req_ids.join(", ") || "none"}
        {data.coverage.unsupported_integrations?.length ? ` — unsupported integrations: ${data.coverage.unsupported_integrations.join(", ")}` : ""}
        {data.coverage.unsupported_ai_use_cases?.length ? ` — unsupported AI: ${data.coverage.unsupported_ai_use_cases.join(", ")}` : ""}</p>}
      <h3>Data domains</h3>
      {data.data_domains?.map((d: any) => (<div key={d.domain_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
        <b>{d.domain_id} — {d.name}</b> <small>owner: {d.ownership} | storage: {d.storage} | reqs: {d.related_req_ids.join(", ")}</small>
        <p>Sources: {d.sources.join(", ")} | Ingestion: {d.ingestion || "—"}</p>
        <p><small>Transactional: {d.storage_transactional || "—"} | Analytical: {d.storage_analytical || "—"} | Metadata: {d.metadata || "—"}</small></p>
        <small>Quality: {d.quality_rules.join("; ") || "—"} | Gov: {d.governance || "—"} | Retention: {d.retention || "—"} | Privacy: {d.privacy || "—"}</small>
        <p><small>Reporting: {d.reporting || "—"} | Backup/Recovery: {d.backup_recovery || "—"}</small></p>
      </div>))}
      <h3>Integrations</h3>
      {data.integrations?.map((i: any) => (<div key={i.int_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
        <b>{i.int_id} — {i.name}</b> [{i.pattern}] <small>{i.source_system} → {i.target_system} | reqs: {i.related_req_ids.join(", ")}</small>
        <p><small>Auth: {i.auth || "—"} | Errors: {i.error_handling || "—"} | Retry: {i.retry || "—"} | Mon: {i.monitoring || "—"} | Sync: {i.sync_notes || "—"}</small></p>
      </div>))}
      <h3>AI use cases</h3>
      {data.ai_use_cases?.map((a: any) => (<div key={a.uc_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
        <b>{a.uc_id} — {a.name}</b> <small>framework: {a.framework} | reqs: {a.related_req_ids.join(", ")}</small>
        <p>AI: {a.ai_function}</p>
        <p><small>Deterministic: {a.deterministic_part || "—"} | Human review: {a.human_review}</small></p>
        <p><small>Why {a.framework}: {a.framework_rationale} | Models: {(a.model_options || []).join(", ") || "—"} | Orchestration: {a.orchestration || "—"} | Prompts: {a.prompt_management || "—"}</small></p>
        <p><small>Retrieval: {a.retrieval_needs || "—"} | Eval: {a.evaluation} | Safety: {a.safety} | Privacy: {a.privacy || "—"} | Mon: {a.monitoring || "—"}</small></p>
      </div>))}
      <h3>Data flow</h3>
      <pre style={{ background: "#f6f6f6", padding: 12, overflowX: "auto" }}>{data.data_flow_mermaid}</pre>
    </div>)}
  </div>);
}
