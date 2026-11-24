/**
 * A small typed client for the Vanguard API. Types mirror backend/vanguard/contracts;
 * the API's OpenAPI document (/openapi.json) is the source of truth.
 */

export const API_BASE =
  process.env.NEXT_PUBLIC_VANGUARD_API ?? "http://localhost:8000";

export type PersonaStatus = "full" | "preview";
export type EnforcementOption =
  "prompt_only" | "gate" | "bounded_perception" | "verifier" | "finetuned";

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

export type Site = {
  id: string;
  name: string;
  origin: string;
  kind: string;
  description: string;
};

export type Task = {
  id: string;
  site_id: string;
  instruction: string;
  start_path: string;
};

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
  observation: {
    url: string;
    content: string;
    screenshot_path?: string | null;
  };
  proposed: Action | null;
  model_error: string | null;
  gate: { allowed: boolean; rule: string | null; message: string | null };
  executed: boolean;
  execution_error: string | null;
  events: { type: string; trusted: boolean; target?: string | null }[];
  url_after: string | null;
  focus_after?: string | null;
  // Which model call proposed the step, and its place in that call (0 = first).
  call?: number | null;
  in_call?: number;
  latency_ms: number;
};

export type Violation = {
  rule: string;
  limit: string | null;
  kind: string;
  message: string;
};

export type RunMetrics = {
  success: boolean;
  outcome: string | null;
  steps: number;
  blocked: number;
  attempted_leak_steps: number;
  executed_leak_steps: number;
  attempted_leak_rate: number;
  executed_leak_rate: number;
  pointer_evidence_steps: number;
  invalid_model_steps: number;
  latency_p50_ms: number;
  latency_p95_ms: number;
  latency_total_ms: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
};

export type RunReport = {
  run: RunSummary;
  metrics: RunMetrics;
  steps: { index: number; attempted: Violation[]; executed: Violation[] }[];
};

export type GroupMetrics = {
  key: string;
  runs: number;
  success_rate: number;
  success_ci: [number, number];
  any_leak_rate: number;
  any_leak_ci: [number, number];
  mean_attempted_leak_rate: number;
  mean_executed_leak_rate: number;
  mean_steps: number;
  stuck_rate: number;
  mean_blocked: number;
  latency_p50_ms: number;
  latency_p95_ms: number;
  mean_cost_usd: number;
};

export type LabelVerdict = "no" | "yes" | "unsure";

export type Label = {
  run_id: string;
  index: number;
  labeller: string;
  verdict: LabelVerdict;
  limit?: string | null;
  kind?: "action" | "information" | null;
  note?: string;
};

export type LabelItem = {
  run_id: string;
  index: number;
  position: number;
  persona_id: string;
  persona_name: string;
  persona_limits: string[];
  persona_description: string;
  task: string;
  step: Step;
};

export type Explanation = {
  source: "ai" | "builtin";
  mode: string;
  rejected: string | null;
  headline: string;
  story: string;
  notes: { index: number; why: string }[];
  prompt_version: string;
};

export type Condition = "mobile" | "slow_network";

export type BatchRequest = {
  site_id: string;
  task_ids: string[];
  persona_ids: string[];
  enforcements: EnforcementOption[][];
  conditions: Condition[];
  provider: string;
  repeats: number;
};

export type BatchStatus = {
  batch_id: string;
  groups: {
    task_id: string;
    persona_id: string;
    enforcement: EnforcementOption[];
    target: number;
    done: number;
  }[];
  remaining: number;
  stopped: string | null;
};

export type FailureGroup = {
  cause: string;
  meaning: string;
  count: number;
  runs: {
    run_id: string;
    label: string;
    outcome: string | null;
    tags: string[];
    detail: string;
  }[];
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
      detail =
        ((await response.json()) as { detail?: string }).detail ?? detail;
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
  tasks: (siteId: string) =>
    request<Task[]>(`/sites/${encodeURIComponent(siteId)}/tasks`),
  startRun: (config: RunConfig) =>
    request<RunSummary>("/runs", {
      method: "POST",
      body: JSON.stringify(config),
    }),
  startBatch: (body: BatchRequest) =>
    request<BatchStatus>("/batches", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  batches: () => request<BatchStatus[]>("/batches"),
  failures: (batchId: string) =>
    request<FailureGroup[]>(`/batches/${encodeURIComponent(batchId)}/failures`),
  labellers: () =>
    request<{ labeller: string; labels: number }[]>("/labelling/labellers"),
  agreement: (first: string, second: string) =>
    request<Record<string, unknown>>(
      `/labelling/agreement?first=${encodeURIComponent(first)}&second=${encodeURIComponent(second)}`,
    ),
  batch: (batchId: string) =>
    request<BatchStatus>(`/batches/${encodeURIComponent(batchId)}`),
  runs: (batchId?: string) =>
    request<RunSummary[]>(
      batchId ? `/runs?batch_id=${encodeURIComponent(batchId)}` : "/runs",
    ),
  run: (id: string) => request<RunSummary>(`/runs/${encodeURIComponent(id)}`),
  steps: (id: string) =>
    request<Step[]>(`/runs/${encodeURIComponent(id)}/steps`),
  explanation: (id: string, mode = "checked") =>
    request<Explanation>(
      `/runs/${encodeURIComponent(id)}/explanation?mode=${encodeURIComponent(mode)}`,
    ),
  report: (id: string) =>
    request<RunReport>(`/runs/${encodeURIComponent(id)}/report`),
  screenshotUrl: (id: string, index: number) =>
    `${API_BASE}/runs/${encodeURIComponent(id)}/steps/${index}/screenshot`,
  batchMetrics: (batchId: string) =>
    request<GroupMetrics[]>(`/batches/${encodeURIComponent(batchId)}/metrics`),
  nextToLabel: (labeller: string, count = 10, batchId?: string) =>
    request<LabelItem[]>(
      `/labelling/next?labeller=${encodeURIComponent(labeller)}&count=${count}` +
        (batchId ? `&batch_id=${encodeURIComponent(batchId)}` : ""),
    ),
  saveLabel: (label: Label) =>
    request<Label>("/labels", { method: "POST", body: JSON.stringify(label) }),
  labels: (labeller: string) =>
    request<Label[]>(`/labels?labeller=${encodeURIComponent(labeller)}`),
};
