"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "../../../components/AppShell";
import { Icon } from "../../../components/Icon";
import { Button } from "../../../components/Primitives";
import { api } from "../../../lib/api";
import { scenarios } from "../../../lib/catalog";
import { useAuthToken } from "../../../lib/auth";
import { can } from "../../../lib/rbac";

type Cloud = "aws" | "azure" | "gcp" | "auto";

export default function NewSessionPage() {
  const router = useRouter();
  const { token, user } = useAuthToken();
  const [step, setStep] = useState(1);
  const [title, setTitle] = useState("");
  const [customer, setCustomer] = useState("");
  const [engagementType, setEngagementType] = useState("RFP");
  const [description, setDescription] = useState("");
  const [cloud, setCloud] = useState<Cloud>("auto");
  const [timeline, setTimeline] = useState("6-12 months");
  const [currency, setCurrency] = useState("INR");
  const [context, setContext] = useState("");
  const [requirements, setRequirements] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  async function createAndAnalyze() {
    if (!token) {
      setStatus("Please login first.");
      return;
    }
    if (!can(user?.role, "createSession") || !can(user?.role, "ingestAnalyze")) {
      setStatus("Your role cannot create and analyze scoping sessions.");
      return;
    }
    if (!title.trim() || !customer.trim() || (!requirements.trim() && !file)) {
      setStatus("Session name, customer and requirements input are required.");
      return;
    }
    setBusy(true);
    setStatus("");
    try {
      const created = await api(
        "/sessions",
        {
          method: "POST",
          body: JSON.stringify({
            title,
            opportunity_context: { customer, engagement_type: engagementType, description, cloud, timeline, currency, context },
          }),
        },
        token,
      );
      const body = new FormData();
      body.append("text", requirements);
      if (file) body.append("file", file);
      await api(`/sessions/${created.id}/ingest`, { method: "POST", body }, token);
      await api(`/sessions/${created.id}/analyze`, { method: "POST" }, token);
      router.push(`/requirements/${created.id}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to create session.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Create a New Scoping Session</h1>
          <div className="eyebrow">Start by providing basic information about this opportunity. You can edit these details later.</div>
        </div>
      </div>

      <div className="create-layout">
        <section className="card pad">
          <div className="split">
            <div className="stack">
              {[
                ["Basic Details", "Opportunity information"],
                ["Upload Requirements", "Add or paste customer inputs"],
                ["Review & Process", "Confirm and analyze"],
              ].map(([label, text], index) => (
                <button className={`option-card ${step === index + 1 ? "active" : ""}`} type="button" onClick={() => setStep(index + 1)} key={label}>
                  <span className="step-number" style={{ width: 34, height: 34 }}>
                    {index + 1}
                  </span>
                  <span>
                    {label}
                    <div className="subtle">{text}</div>
                  </span>
                </button>
              ))}
            </div>

            <div>
              {step === 1 && (
                <div className="grid">
                  <div>
                    <h2 className="card-title">Basic Details</h2>
                    <div className="subtle">Provide key information about the customer opportunity.</div>
                  </div>
                  <div className="form-grid">
                    <label className="field full">
                      <span className="label">Session Name *</span>
                      <input className="input" value={title} onChange={(event) => setTitle(event.target.value)} />
                    </label>
                    <label className="field">
                      <span className="label">Customer / Opportunity *</span>
                      <input className="input" value={customer} onChange={(event) => setCustomer(event.target.value)} />
                    </label>
                    <label className="field">
                      <span className="label">Engagement Type *</span>
                      <select className="select" value={engagementType} onChange={(event) => setEngagementType(event.target.value)}>
                        <option>RFP</option>
                        <option>Discovery Call</option>
                        <option>Internal Initiative</option>
                        <option>Other</option>
                      </select>
                    </label>
                    <label className="field full">
                      <span className="label">Description</span>
                      <textarea className="textarea" value={description} onChange={(event) => setDescription(event.target.value)} />
                    </label>
                    <div className="field full">
                      <span className="label">Target Cloud</span>
                      <div className="cloud-options">
                        {[
                          ["aws", "AWS"],
                          ["azure", "Azure"],
                          ["gcp", "GCP"],
                          ["auto", "To be decided"],
                        ].map(([value, label]) => (
                          <button className={`option-card ${cloud === value ? "active" : ""}`} type="button" onClick={() => setCloud(value as Cloud)} key={value}>
                            {label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <label className="field">
                      <span className="label">Estimated Timeline</span>
                      <select className="select" value={timeline} onChange={(event) => setTimeline(event.target.value)}>
                        <option>3-6 months</option>
                        <option>6-12 months</option>
                        <option>12+ months</option>
                      </select>
                    </label>
                    <label className="field">
                      <span className="label">Currency</span>
                      <select className="select" value={currency} onChange={(event) => setCurrency(event.target.value)}>
                        <option>INR</option>
                        <option>USD</option>
                        <option>EUR</option>
                      </select>
                    </label>
                    <label className="field full">
                      <span className="label">Additional Context</span>
                      <textarea className="textarea" value={context} onChange={(event) => setContext(event.target.value)} placeholder="Known constraints, existing systems, strategic priorities, or other context." />
                    </label>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="grid">
                  <div>
                    <h2 className="card-title">Upload Requirements</h2>
                    <div className="subtle">Paste customer inputs or upload a PDF, DOCX, TXT or Markdown file.</div>
                  </div>
                  <label className="field">
                    <span className="label">Requirements Text</span>
                    <textarea className="textarea" style={{ minHeight: 220 }} value={requirements} onChange={(event) => setRequirements(event.target.value)} />
                  </label>
                  <label className="field">
                    <span className="label">Requirement File</span>
                    <input className="input" type="file" accept=".pdf,.docx,.txt,.md" onChange={(event) => setFile(event.target.files?.[0] || null)} />
                  </label>
                </div>
              )}

              {step === 3 && (
                <div className="grid">
                  <div>
                    <h2 className="card-title">Review & Process</h2>
                    <div className="subtle">Confirm the details, then create the session and queue analysis.</div>
                  </div>
                  <div className="success-box">
                    <strong>{title}</strong>
                    <div>{customer} | {engagementType} | {cloud.toUpperCase()} | {timeline}</div>
                  </div>
                  <div className="success-box">Signed in as {user?.email} with {user?.role} access.</div>
                  {status && <div className="alert-box">{status}</div>}
                </div>
              )}
            </div>
          </div>
        </section>

        <aside className="grid">
          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Need Inspiration?</h2>
              <button className="btn ghost" type="button">
                View All Scenarios
              </button>
            </div>
            <div className="stack">
              {scenarios.map((scenario) => (
                <div className="scenario-card" key={scenario.name}>
                  <span className="icon-wrap">
                    <Icon name={scenario.icon} />
                  </span>
                  <div>
                    <strong>{scenario.name}</strong> <span className="badge blue">{scenario.tag}</span>
                    <div className="subtle">{scenario.text}</div>
                  </div>
                  <button
                    className="btn ghost"
                    type="button"
                    onClick={() => {
                      setTitle(scenario.name);
                      setEngagementType(scenario.tag);
                      setDescription(scenario.text);
                      setRequirements(scenario.text);
                    }}
                  >
                    Use This
                  </button>
                </div>
              ))}
            </div>
          </section>

          <section className="card pad" style={{ background: "#edf6ff" }}>
            <div className="card-header">
              <span className="icon-wrap">
                <Icon name="help" />
              </span>
              <h2 className="card-title">What happens next?</h2>
            </div>
            <div className="stack">
              {["Upload or paste customer requirements", "AI will extract and structure requirements", "Review, edit and approve extracted requirements", "Generate PRD, solution design, estimates and package"].map((item, index) => (
                <div className="activity-item" key={item}>
                  <span className="step-number" style={{ width: 30, height: 30 }}>
                    {index + 1}
                  </span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>

      <div className="card pad" style={{ marginTop: 18, display: "flex", justifyContent: "flex-end", gap: 12 }}>
        <button className="btn" type="button" onClick={() => router.push("/sessions")}>
          Cancel
        </button>
        {step < 3 ? (
          <Button onClick={() => setStep(step + 1)}>
            Next
            <Icon name="arrow" />
          </Button>
        ) : (
          <Button onClick={createAndAnalyze} disabled={busy}>
            <Icon name="spark" />
            {busy ? "Processing..." : "Create & Analyze"}
          </Button>
        )}
      </div>
    </AppShell>
  );
}
