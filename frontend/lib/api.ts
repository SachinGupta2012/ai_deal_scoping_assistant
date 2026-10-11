const configuredApi = process.env.NEXT_PUBLIC_API_URL;

function apiBase(): string {
  if (configuredApi) return configuredApi;
  if (typeof window !== "undefined") {
    return `${window.location.protocol}//${window.location.hostname}:8000`;
  }
  return "http://127.0.0.1:8000";
}

export async function api(path: string, opts: RequestInit = {}, token?: string) {
  const headers: Record<string, string> = { ...(opts.headers as object || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (opts.body && typeof opts.body === "string" && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const res = await fetch(`${apiBase()}${path}`, { ...opts, headers });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}
