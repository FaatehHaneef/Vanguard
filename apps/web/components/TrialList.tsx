"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type RunSummary } from "@/lib/api";
import { characterFor } from "@/lib/cast";

/** Every trial so far, newest first. A trial is the set of runs started together. */
export function TrialList() {
  const [runs, setRuns] = useState<RunSummary[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .runs()
      .then(setRuns)
      .catch(() => setError("The Vanguard API is not reachable."));
  }, []);

  if (error) return <p className="font-bold text-rose">{error}</p>;
  if (runs === null) return <p className="text-mist">Loading…</p>;
  if (runs.length === 0) return <p className="text-mist">No trials yet.</p>;

  const batches = new Map<string, RunSummary[]>();
  for (const run of runs) {
    const key = run.config.batch_id ?? run.id;
    batches.set(key, [...(batches.get(key) ?? []), run]);
  }

  return (
    <ul className="grid gap-3">
      {[...batches.entries()].map(([batch, members]) => {
        const first = members[members.length - 1];
        const names = [
          ...new Set(members.map((run) => characterFor(run.config.persona_id)?.name ?? "?")),
        ];
        const succeeded = members.filter((run) => run.outcome === "success").length;
        return (
          <li key={batch}>
            <Link href={`/trials/${batch}`} className="pixel-panel flex flex-wrap gap-x-4 p-4">
              <span className="font-display font-bold text-parchment">{names.join(", ")}</span>
              <span className="text-parchment">
                {first.config.task_id} on {first.config.site_id}
              </span>
              <span className="text-mist">
                {succeeded} of {members.length} completed ·{" "}
                {new Date(first.created_at).toLocaleString()}
              </span>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
