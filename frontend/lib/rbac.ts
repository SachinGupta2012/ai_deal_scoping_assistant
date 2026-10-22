import type { UserRole } from "./auth";

const permissions: Record<string, readonly UserRole[]> = {
  createSession: ["admin", "sales", "architect", "ba", "delivery", "reviewer"],
  ingestAnalyze: ["admin", "sales", "architect", "ba"],
  editScope: ["admin", "architect", "ba", "reviewer"],
  approveScope: ["admin", "architect", "reviewer"],
  generatePrd: ["admin", "architect", "ba", "reviewer"],
  generateArchitecture: ["admin", "architect", "reviewer"],
  generateDataAi: ["admin", "architect", "ba", "reviewer"],
  estimate: ["admin", "architect", "delivery", "reviewer"],
  exportPackage: ["admin", "architect", "delivery", "reviewer"],
  manageUsers: ["admin"],
};

export type Permission = keyof typeof permissions;

export function can(role: UserRole | undefined, permission: Permission) {
  return Boolean(role && permissions[permission].includes(role));
}

export const roleDescriptions: Record<UserRole, string> = {
  admin: "Manage users and all workflow actions.",
  sales: "Create sessions, ingest requirements and run initial analysis.",
  architect: "Own scope approval, PRD, architecture, data/AI, estimates and export.",
  ba: "Create sessions, analyze requirements, edit scope and generate PRD/data strategy.",
  delivery: "Create sessions and work on estimates, impact, validation and export.",
  reviewer: "Review and approve scope, solution outputs, estimates and final package.",
  viewer: "Read-only access to generated outputs.",
};
