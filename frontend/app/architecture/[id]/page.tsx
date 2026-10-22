"use client";

import { useState } from "react";
import { AppShell } from "../../../components/AppShell";
import { Icon } from "../../../components/Icon";
import { Button } from "../../../components/Primitives";
import { EmptyState, WorkspaceFrame } from "../../../components/Workspace";
import { MermaidPreview } from "../../../lib/MermaidPreview";
import { api } from "../../../lib/api";
import { useAuthToken } from "../../../lib/auth";
import { can } from "../../../lib/rbac";

type ComponentItem = {
  component_id: string;
  name: string;
  layer: string;
  cloud_service: string;
  purpose: string;
  rationale: string;
  tradeoffs?: string;
  supported_req_ids: string[];
  security?: string;
};

export default function ArchPage({ params }: { params: { id: string } }) {
  const { token, user } = useAuthToken();
  const [platform, setPlatform] = useState("auto");
  const [arch, setArch] = useState<any>(null);
  const [status, setStatus] = useState("");
  const canGenerate = can(user?.role, "generateArchitecture");

  async function generate() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/architecture`, { method: "POST", body: JSON.stringify({ platform }) }, token);
      setStatus(`Architecture queued for ${result.platform}. Refresh in a few seconds.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to generate architecture.");
    }
  }

  async function refresh() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/architecture`, {}, token);
      setArch(result.architecture || null);
      if (!result.architecture) setStatus("Pending. Approve scope and generate architecture first.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to refresh architecture.");
    }
  }

  return (
    <AppShell sessionId={params.id}>
      <WorkspaceFrame
        sessionId={params.id}
        title="Solution Design"
        subtitle="Create a cloud-specific architecture with traceable components, tradeoffs and diagram preview."
        active="architecture"
        actions={
          <div className="filter-row">
            <Button onClick={generate} disabled={!canGenerate}>
              <Icon name="design" />
              Generate Architecture
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
              <select className="select" value={platform} onChange={(event) => setPlatform(event.target.value)} style={{ width: 180 }}>
                <option value="auto">Auto-recommend</option>
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">GCP</option>
              </select>
            </div>
          </section>

          {status && <div className="alert-box">{status}</div>}
          {!arch ? (
            <EmptyState title="No architecture yet" text="Generate architecture after scope approval." />
          ) : (
            <>
              <section className="card pad">
                <div className="card-header">
                  <div>
                    <h2 className="card-title">Recommended Platform: {arch.platform}</h2>
                    <div className="subtle">{arch.platform_rationale}</div>
                  </div>
                  <span className="badge green">Catalog checked</span>
                </div>
                {arch.validation?.off_catalog?.length ? <div className="alert-box">Off-catalog: {arch.validation.off_catalog.join(", ")}</div> : null}
                {arch.validation?.missing_layers?.length ? <div className="alert-box">Missing layers: {arch.validation.missing_layers.join(", ")}</div> : null}
                <MermaidPreview source={arch.mermaid} />
              </section>

              <section className="card pad">
                <div className="card-header">
                  <h2 className="card-title">Architecture Components</h2>
                  <span className="subtle">{arch.components?.length || 0} components</span>
                </div>
                <div className="stack">
                  {(arch.components || []).map((component: ComponentItem) => (
                    <div className="scenario-card" key={component.component_id}>
                      <span className="icon-wrap">
                        <Icon name="design" />
                      </span>
                      <div>
                        <strong>{component.component_id} - {component.name}</strong>
                        <div className="subtle">{component.layer} | {component.cloud_service} | Reqs: {component.supported_req_ids.join(", ")}</div>
                        <p>{component.purpose}</p>
                        <div className="subtle">Rationale: {component.rationale}</div>
                        <div className="subtle">Tradeoffs: {component.tradeoffs || "-"} | Security: {component.security || "-"}</div>
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
