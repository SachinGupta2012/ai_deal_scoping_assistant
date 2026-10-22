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

export default function DataAiPage({ params }: { params: { id: string } }) {
  const { token, user } = useAuthToken();
  const [data, setData] = useState<any>(null);
  const [status, setStatus] = useState("");
  const canGenerate = can(user?.role, "generateDataAi");

  async function generate() {
    setStatus("");
    try {
      await api(`/sessions/${params.id}/data-ai`, { method: "POST" }, token);
      setStatus("Data, integration and AI strategy queued. Refresh in a few seconds.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to generate strategy.");
    }
  }

  async function refresh() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/data-ai`, {}, token);
      setData(result.data_ai || null);
      if (!result.data_ai) setStatus("Pending. Approve scope and generate strategy first.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to refresh strategy.");
    }
  }

  return (
    <AppShell sessionId={params.id}>
      <WorkspaceFrame
        sessionId={params.id}
        title="Data, Integration & AI"
        subtitle="Plan data domains, integrations, AI use cases, governance, safety and flow."
        active="data-ai"
        actions={
          <div className="filter-row">
            <Button onClick={generate} disabled={!canGenerate}>
              <Icon name="data" />
              Generate Strategy
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
              {data?.coverage && <span className="badge green">Coverage {data.coverage.coverage_pct}%</span>}
            </div>
          </section>

          {status && <div className="alert-box">{status}</div>}
          {!data ? (
            <EmptyState title="No data strategy yet" text="Generate this workspace after scope approval." />
          ) : (
            <>
              <section className="card pad">
                <div className="card-header">
                  <h2 className="card-title">Coverage</h2>
                  <span className="subtle">Uncovered: {data.coverage?.uncovered_req_ids?.join(", ") || "none"}</span>
                </div>
                <MermaidPreview source={data.data_flow_mermaid} />
              </section>

              <div className="split">
                <section className="card pad">
                  <h2 className="card-title">Data Domains</h2>
                  <div className="stack" style={{ marginTop: 16 }}>
                    {(data.data_domains || []).map((domain: any) => (
                      <div className="scenario-card" key={domain.domain_id}>
                        <span className="icon-wrap success">
                          <Icon name="data" />
                        </span>
                        <div>
                          <strong>{domain.domain_id} - {domain.name}</strong>
                          <div className="subtle">Owner: {domain.ownership} | Storage: {domain.storage}</div>
                          <p>Sources: {(domain.sources || []).join(", ")} | Ingestion: {domain.ingestion || "-"}</p>
                          <div className="subtle">Quality: {(domain.quality_rules || []).join("; ") || "-"} | Privacy: {domain.privacy || "-"}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>

                <section className="card pad">
                  <h2 className="card-title">Integrations</h2>
                  <div className="stack" style={{ marginTop: 16 }}>
                    {(data.integrations || []).map((integration: any) => (
                      <div className="scenario-card" key={integration.int_id}>
                        <span className="icon-wrap purple">
                          <Icon name="change" />
                        </span>
                        <div>
                          <strong>{integration.int_id} - {integration.name}</strong>
                          <div className="subtle">{integration.source_system} to {integration.target_system} | {integration.pattern}</div>
                          <p>Auth: {integration.auth || "-"} | Retry: {integration.retry || "-"} | Monitoring: {integration.monitoring || "-"}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>

              <section className="card pad">
                <div className="card-header">
                  <h2 className="card-title">AI Use Cases</h2>
                  <span className="subtle">{data.ai_use_cases?.length || 0} identified</span>
                </div>
                <div className="stack">
                  {(data.ai_use_cases || []).map((useCase: any) => (
                    <div className="scenario-card" key={useCase.uc_id}>
                      <span className="icon-wrap">
                        <Icon name="spark" />
                      </span>
                      <div>
                        <strong>{useCase.uc_id} - {useCase.name}</strong>
                        <div className="subtle">Framework: {useCase.framework} | Reqs: {(useCase.related_req_ids || []).join(", ")}</div>
                        <p>{useCase.ai_function}</p>
                        <div className="subtle">Evaluation: {useCase.evaluation} | Safety: {useCase.safety} | Human review: {useCase.human_review}</div>
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
