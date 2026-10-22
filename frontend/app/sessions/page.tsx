import Link from "next/link";
import { AppShell } from "../../components/AppShell";
import { Icon } from "../../components/Icon";
import { ButtonLink } from "../../components/Primitives";
import { SessionsClient } from "../../components/SessionsClient";

export default function SessionsPage() {
  return (
    <AppShell>
      <div className="page-header">
        <div>
          <h1 className="page-title">Scoping Sessions</h1>
          <div className="eyebrow">Manage all deal scoping sessions, from initial analysis to final export.</div>
        </div>
        <ButtonLink href="/sessions/new">
          <Icon name="plus" />
          New Scoping Session
        </ButtonLink>
      </div>

      <div className="sessions-layout">
        <SessionsClient />

        <aside className="grid">
          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Session Statistics</h2>
              <select className="select" style={{ width: 130 }} defaultValue="30">
                <option value="30">Last 30 Days</option>
              </select>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "130px 1fr", gap: 18, alignItems: "center" }}>
              <div style={{ width: 118, height: 118, borderRadius: "999px", background: "conic-gradient(#0057ff 0 42%, #34d399 42% 74%, #fb7185 74% 100%)", display: "grid", placeItems: "center" }}>
                <div style={{ width: 70, height: 70, borderRadius: "999px", background: "#fff", display: "grid", placeItems: "center", fontWeight: 800 }}>12</div>
              </div>
              <div className="stack">
                {["In Progress 5", "Completed 4", "Needs Review 3", "Not Started 0"].map((item) => (
                  <div className="card-header" style={{ marginBottom: 0 }} key={item}>
                    <span>{item.replace(/\s\d+$/, "")}</span>
                    <strong>{item.match(/\d+$/)?.[0]}</strong>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Quick Filters</h2>
              <Icon name="chevron" />
            </div>
            <div className="stack">
              {["In Progress", "Completed", "Needs Review", "Not Started", "RFP", "Discovery Call", "Internal Initiative"].map((label) => (
                <label className="attention-item" key={label}>
                  <span>
                    <input type="checkbox" defaultChecked={label === "In Progress"} /> {label}
                  </span>
                  <span className="badge gray">{label === "In Progress" ? 5 : label === "Completed" ? 4 : label === "Needs Review" ? 3 : 1}</span>
                </label>
              ))}
            </div>
          </section>

          <section className="card pad">
            <div className="card-header">
              <h2 className="card-title">Recent Activity</h2>
              <Link className="link-text" href="/dashboard">
                View All
              </Link>
            </div>
            <div className="subtle">Activity will appear here after live sessions are processed.</div>
          </section>
        </aside>
      </div>
    </AppShell>
  );
}
