import Link from "next/link";
import type { ReactNode } from "react";

const tabs = [
  ["Requirements", "requirements"],
  ["PRD & Scope", "prd"],
  ["Architecture", "architecture"],
  ["Data & AI", "data-ai"],
  ["Estimation", "estimate"],
  ["Package", "package"],
];

export function WorkspaceFrame({ sessionId, title, subtitle, active, actions, children }: { sessionId: string; title: string; subtitle: string; active: string; actions?: ReactNode; children: ReactNode }) {
  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">{title}</h1>
          <div className="eyebrow">{subtitle}</div>
        </div>
        {actions}
      </div>
      <div className="workspace-tabs">
        {tabs.map(([label, route]) => (
          <Link className={`workspace-tab ${route === active ? "active" : ""}`} href={`/${route}/${sessionId}`} key={route}>
            {label}
          </Link>
        ))}
      </div>
      {children}
    </>
  );
}

export function EmptyState({ title, text }: { title: string; text: string }) {
  return (
    <div className="card pad">
      <h3 className="card-title">{title}</h3>
      <p className="eyebrow">{text}</p>
    </div>
  );
}
