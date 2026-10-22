import { z } from "zod";
export const RequirementSchema = z.object({
  req_id: z.string(), type: z.string(), description: z.string(),
  priority: z.string(), chunk_id: z.string(), quote: z.string(),
  origin: z.enum(["customer-stated", "AI-inferred", "assumed"]),
  dependencies: z.array(z.string()).default([]), questions: z.array(z.string()).default([]),
});
export const ScopeSchema = z.object({
  version_no: z.number().optional(), status: z.string().optional(),
  scope: z.object({ requirements: z.array(RequirementSchema), assumptions: z.array(z.any()).default([]), questions: z.array(z.any()).default([]) }).passthrough(),
});
export type Scope = z.infer<typeof ScopeSchema>;
