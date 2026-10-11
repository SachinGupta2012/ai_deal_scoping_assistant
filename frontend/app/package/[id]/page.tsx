"use client";

import { useState } from "react";
import { AppShell } from "../../../components/AppShell";
import { Icon } from "../../../components/Icon";
import { Button } from "../../../components/Primitives";
import { WorkspaceFrame } from "../../../components/Workspace";
import { api } from "../../../lib/api";
import { useAuthToken } from "../../../lib/auth";
import { can } from "../../../lib/rbac";

export default function PackagePage({ params }: { params: { id: string } }) {
  const { token, user } = useAuthToken();
  const [changedReqIds, setChangedReqIds] = useState("");
  const [changedAssumptionIds, setChangedAssumptionIds] = useState("");
  const [gate, setGate] = useState<any>(null);
  const [impact, setImpact] = useState<any>(null);
  const [pkg, setPkg] = useState<any>(null);
  const [status, setStatus] = useState("");
  const canExport = can(user?.role, "exportPackage");
  const impactBody = {
    changed_req_ids: changedReqIds.split(",").map((item) => item.trim()).filter(Boolean),
    changed_assumption_ids: changedAssumptionIds.split(",").map((item) => item.trim()).filter(Boolean),
    config_changes: {},
  };

  async function reviewImpact() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/change-impact`, { method: "POST", body: JSON.stringify(impactBody) }, token);
      setImpact(result.change_impact);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to review impact.");
    }
  }

  async function runGate() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/quality-gate`, { method: "POST" }, token);
      setGate(result.quality_gate);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to run quality gate.");
    }
  }

  async function exportPackage() {
    setStatus("");
    try {
      const result = await api(`/sessions/${params.id}/package`, { method: "POST", body: JSON.stringify(impactBody) }, token);
      setPkg(result.package);
      setGate(result.package.quality_gate);
      setImpact(result.package.change_impact);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to export package.");
    }
  }

  function downloadMarkdown() {
    if (!pkg?.markdown) return;
    const blob = new Blob([pkg.markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `scoping-package-${params.id}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <AppShell sessionId={params.id}>
      <WorkspaceFrame
        sessionId={params.id}
        title="Validation & Export"
        subtitle="Review change impact, run quality checks and export the final package with mandatory disclaimer."
        active="package"
        actions={
          <div className="filter-row">
            <Button onClick={reviewImpact} disabled={!canExport}>
              <Icon name="change" />
              Review Impact
            </Button>
            <Button variant="ghost" onClick={runGate} disabled={!canExport}>
              <Icon name="shield" />
              Quality Gate
            </Button>
            <Button variant="ghost" onClick={exportPackage} disabled={!canExport}>
              <Icon name="export" />
              Export Package
            </Button>
          </div>
        }
      >
        <div className="grid">
          <section className="card pad">
            <div className="form-grid">
              <div className="success-box">Signed in as {user?.email} with {user?.role} access.</div>
              <label className="field">
                <span className="label">Changed Requirement IDs</span>
                <input className="input" value={changedReqIds} onChange={(event) => setChangedReqIds(event.target.value)} placeholder="NFR_01, INT_01" />
              </label>
              <label className="field">
                <span className="label">Changed Assumption IDs</span>
                <input className="input" value={changedAssumptionIds} onChange={(event) => setChangedAssumptionIds(event.target.value)} placeholder="ASM_01" />
              </label>
            </div>
          </section>

          {status && <div className="alert-box">{status}</div>}

          <div className="split">
            <section className="card pad">
              <div className="card-header">
                <h2 className="card-title">Change Impact</h2>
                {impact && <span className="badge blue">{impact.affected_outputs?.length || 0} outputs</span>}
              </div>
              {!impact ? (
                <p className="eyebrow">Enter changed IDs and run impact review.</p>
              ) : (
                <div className="stack">
                  <div className="attention-item"><strong>Affected outputs</strong><span>{impact.affected_outputs?.join(", ") || "none"}</span></div>
                  <div className="attention-item"><strong>Affected reqs</strong><span>{impact.affected_req_ids?.join(", ") || "none"}</span></div>
                  <div className="attention-item"><strong>Unaffected reqs</strong><span>{impact.unaffected_req_ids?.join(", ") || "none"}</span></div>
                  <div className="attention-item"><strong>Components</strong><span>{impact.affected_component_ids?.join(", ") || "-"}</span></div>
                  <div className="attention-item"><strong>Workstreams</strong><span>{impact.affected_workstream_ids?.join(", ") || "-"}</span></div>
                </div>
              )}
            </section>

            <section className="card pad">
              <div className="card-header">
                <h2 className="card-title">Quality Gate</h2>
                {gate && <span className={`badge ${gate.status === "pass" ? "green" : "red"}`}>{gate.status}</span>}
              </div>
              {!gate ? (
                <p className="eyebrow">Run quality gate to check coverage, consistency and export readiness.</p>
              ) : (
                <div className="stack">
                  <p>{gate.summary}</p>
                  {(gate.issues || []).map((issue: any) => (
                    <div className="attention-item" key={issue.issue_id}>
                      <span><strong>{issue.issue_id}</strong> {issue.category}: {issue.message}</span>
                      <span className={`badge ${issue.severity === "high" ? "red" : "gray"}`}>{issue.severity}</span>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>

          {pkg && (
            <section className="card pad">
              <div className="card-header">
                <div>
                  <h2 className="card-title">Package Export</h2>
                  <div className="subtle">Saved: {pkg.export_path}</div>
                </div>
                <Button onClick={downloadMarkdown}>
                  <Icon name="export" />
                  Download Markdown
                </Button>
              </div>
              <div className="alert-box">
                Mandatory disclaimer is included in the exported package. Review assumptions, risks and open questions before customer use.
              </div>
              <pre style={{ background: "#f6f9fe", border: "1px solid #dbe6f4", borderRadius: 8, padding: 16, overflowX: "auto", whiteSpace: "pre-wrap" }}>{pkg.markdown}</pre>
            </section>
          )}
        </div>
      </WorkspaceFrame>
    </AppShell>
  );
}
