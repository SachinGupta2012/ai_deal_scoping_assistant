"use client";

type Edge = { from: string; fromLabel: string; to: string; toLabel: string };

function parseNode(raw: string) {
  const trimmed = raw.trim().replace(/;$/, "");
  const match = trimmed.match(/^([A-Za-z0-9_]+)\[(.+)\]$/);
  if (match) return { id: match[1], label: match[2] };
  return { id: trimmed, label: trimmed };
}

function parseEdges(source: string): Edge[] {
  return source.split("\n").filter(line => line.includes("-->")).map(line => {
    const [left, right] = line.split("-->");
    const from = parseNode(left);
    const to = parseNode(right);
    return { from: from.id, fromLabel: from.label, to: to.id, toLabel: to.label };
  });
}

export function MermaidPreview({ source }: { source: string }) {
  const edges = parseEdges(source || "");
  if (!edges.length) return null;
  return (<div style={{ display: "grid", gap: 8, margin: "12px 0" }}>
    {edges.map((edge, idx) => (
      <div key={`${edge.from}-${edge.to}-${idx}`} style={{ display: "grid", gridTemplateColumns: "1fr 48px 1fr", alignItems: "center", gap: 8 }}>
        <div style={{ border: "1px solid #ccc", padding: 10, borderRadius: 6, background: "#fff" }}><b>{edge.from}</b><br /><small>{edge.fromLabel}</small></div>
        <div style={{ textAlign: "center", color: "#555" }}>to</div>
        <div style={{ border: "1px solid #ccc", padding: 10, borderRadius: 6, background: "#fff" }}><b>{edge.to}</b><br /><small>{edge.toLabel}</small></div>
      </div>
    ))}
  </div>);
}
