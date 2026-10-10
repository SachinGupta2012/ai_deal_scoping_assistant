"use client";
import { useEffect, useState } from "react";
import { api } from "../../../lib/api";

export default function ReqPage({ params }: { params: { id: string } }) {
  const [scope, setScope] = useState<any>(null);
  const [token, setToken] = useState("");
  useEffect(() => {
    if (!token) return;
    const t = setInterval(async () => {
      try { const s = await api(`/sessions/${params.id}/scope`, {}, token); if (s.scope) { setScope(s); clearInterval(t); } } catch {}
    }, 2000);
    return () => clearInterval(t);
  }, [token, params.id]);
  return (<div>
    <h2>Requirements Workspace — {params.id}</h2>
    <input placeholder="paste JWT" value={token} onChange={e => setToken(e.target.value)} style={{ width: "100%" }} />
    <button onClick={async () => { await api(`/sessions/${params.id}/analyze`, { method: "POST" }, token); }}>Analyze Requirements</button>
    {!scope && <p>Waiting for scope…</p>}
    {scope?.scope?.requirements?.map((r: any) => (
      <div key={r.req_id} style={{ border: "1px solid #ddd", padding: 12, margin: "8px 0" }}>
        <b>{r.req_id}</b> [{r.type}] [{r.origin}] <i>{r.priority}</i><p>{r.description}</p>
        <small>src chunk {r.chunk_id}: {r.quote?.slice(0, 160)}</small>
      </div>))}
  </div>);
}
