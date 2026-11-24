/**
 * GET /compare (backend/vanguard/routes/compare.py): two batches side by side. Types
 * mirror backend/vanguard/contracts/compare.py; see docs/checkpoints/CP-G1.md.
 */

import { API_BASE } from "@/lib/api";

export type Verdict = "better" | "worse" | "same" | "only_baseline" | "only_candidate";
export type Match = "full" | "persona_task";

export type GroupSnapshot = {
  runs: number;
  success_rate: number;
  any_leak_rate: number;
  mean_steps: number;
  stuck_rate: number;
  mean_blocked: number;
  mean_cost_usd: number;
  failures: number;
  /** Added once repeated attempts are in the metrics; shown when present. */
  mean_repeated_attempts?: number;
};

export type MetricChange = {
  metric: string;
  baseline: number;
  candidate: number;
  delta: number;
  verdict: Verdict;
};

export type CompareGroup = {
  key: string;
  baseline: GroupSnapshot | null;
  candidate: GroupSnapshot | null;
  changes: MetricChange[];
  verdict: Verdict;
};

export type FailureChange = {
  key: string;
  cause: string;
  meaning: string;
  run_ids: string[];
};

export type Comparison = {
  baseline: string;
  candidate: string;
  match: Match;
  groups: CompareGroup[];
  new_failures: FailureChange[];
  resolved_failures: FailureChange[];
};

export async function fetchComparison(baseline: string, candidate: string, match: Match): Promise<Comparison> {
  const query = new URLSearchParams({ baseline, candidate, match });
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/compare?${query}`, { cache: "no-store" });
  } catch {
    throw new Error("The Vanguard API is not reachable. Is the backend running?");
  }
  if (!response.ok) {
    let detail = `The comparison failed (${response.status}).`;
    try {
      const body = (await response.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // Not JSON: keep the status.
    }
    throw new Error(response.status === 404 ? `${detail}. Only finished runs count.` : detail);
  }
  return (await response.json()) as Comparison;
}
