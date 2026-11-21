/**
 * A small typed client for the Vanguard API. Types mirror backend/vanguard/contracts;
 * the API's OpenAPI document (/openapi.json) is the source of truth.
 */

export const API_BASE = process.env.NEXT_PUBLIC_VANGUARD_API ?? "http://localhost:8000";

export type PersonaStatus = "full" | "preview";
export type EnforcementOption =
  | "prompt_only"
  | "gate"
  | "bounded_perception"
  | "verifier"
  | "finetuned";

export type Persona = {
  id: string;
  name: string;
  character: string;
  represents: string;
  status: PersonaStatus;
  limits: string[];
  perception: string;
  is_control: boolean;
};

export type Site = { id: string; name: string; origin: string; kind: string; description: string };

export type Task = { id: string; site_id: string; instruction: string; start_path: string };

export type RunConfig = {
  site_id: string;
  task_id: string;
  persona_id: string;
  enforcement: EnforcementOption[];
  provider?: string;
  repeat_index?: number;
  batch_id?: string;
};

export type RunSummary = {
  id: string;
  config: RunConfig;
  status: "queued" | "running" | "finished" | "failed";
  outcome: "success" | "gave_up" | "stuck" | "step_limit" | "error" | null;
  steps: number;
  blocked: number;
  error: string | null;
  created_at: string;
  finished_at: string | null;
};

export type Action = {
  tool: string;
  rationale: string;
  [argument: string]: string | number | null | undefined;
};

export type Step = {
  run_id: string;
  index: number;
  observation: { url: string; content: string };
  proposed: Action | null;
  model_error: string | null;
  gate: { allowed: boolean; rule: string | null; message: string | null };
  executed: boolean;
  execution_error: string | null;
  events: { type: string; trusted: boolean }[];
  url_after: string | null;
  latency_ms: number;
};

export type Health = { status: string; providers: string[]; executor: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) {
    let detail = `${response.status}`;
    try {
      detail = ((await response.json()) as { detail?: string }).detail ?? detail;
    } catch {
      // The body was not JSON: keep the status code.
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export const api = {
  health: () => request<Health>("/health"),
  personas: () => request<Persona[]>("/personas"),
  sites: () => request<Site[]>("/sites"),
  tasks: (siteId: string) => request<Task[]>(`/sites/${encodeURIComponent(siteId)}/tasks`),
  startRun: (config: RunConfig) =>
    request<RunSummary>("/runs", { method: "POST", body: JSON.stringify(config) }),
  runs: (batchId?: string) =>
    request<RunSummary[]>(batchId ? `/runs?batch_id=${encodeURIComponent(batchId)}` : "/runs"),
  run: (id: string) => request<RunSummary>(`/runs/${encodeURIComponent(id)}`),
  steps: (id: string) => request<Step[]>(`/runs/${encodeURIComponent(id)}/steps`),
};
