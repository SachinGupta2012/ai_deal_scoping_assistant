const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export async function api(path: string, opts: RequestInit = {}, token?: string) {
  const headers: Record<string, string> = { ...(opts.headers as object || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (opts.body && typeof opts.body === "string" && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const res = await fetch(`${API}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}
