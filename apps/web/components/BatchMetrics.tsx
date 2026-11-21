"use client";

import { useEffect, useState } from "react";
import { api, type GroupMetrics } from "@/lib/api";

function pct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function withInterval(rate: number, ci: [number, number]): string {
  return `${pct(rate)} (${pct(ci[0])}–${pct(ci[1])})`;
}

/**
 * The comparison table for one trial: one row per persona × task × enforcement group.
 * Every number comes from the backend's checker and metrics code.
 */
export function BatchMetrics({
  batchId,
  refreshKey,
}: {
  batchId: string;
  refreshKey: number;
}) {
  const [groups, setGroups] = useState<GroupMetrics[]>([]);

  useEffect(() => {
    let live = true;
    api.batchMetrics(batchId).then(
      (found) => live && setGroups(found),
      () => undefined,
    );
    return () => {
      live = false;
    };
  }, [batchId, refreshKey]);

  if (groups.length === 0) return null;

  return (
    <section
      className="pixel-panel grid gap-3 overflow-x-auto"
      aria-labelledby="compare-title"
    >
      <h2
        id="compare-title"
        className="font-display text-xl font-bold text-amber"
      >
        Comparison
      </h2>
      <table className="w-full text-left text-sm text-parchment">
        <caption className="mb-2 text-left text-mist">
          Finished runs per group. Percentages in brackets are 95% Wilson
          intervals.
        </caption>
        <thead className="text-mist">
          <tr>
            <th scope="col">Persona / task / enforcement</th>
            <th scope="col">Runs</th>
            <th scope="col">Success</th>
            <th scope="col">Runs with a broken limit</th>
            <th scope="col">Tried / step</th>
            <th scope="col">Broke / step</th>
            <th scope="col">Steps</th>
            <th scope="col">Stuck</th>
            <th scope="col">Step time p50 / p95</th>
          </tr>
        </thead>
        <tbody>
          {groups.map((group) => (
            <tr key={group.key} className="border-t border-line/30">
              <th scope="row" className="py-1 font-normal">
                <code>{group.key}</code>
              </th>
              <td>{group.runs}</td>
              <td>{withInterval(group.success_rate, group.success_ci)}</td>
              <td>{withInterval(group.any_leak_rate, group.any_leak_ci)}</td>
              <td>{group.mean_attempted_leak_rate.toFixed(2)}</td>
              <td>{group.mean_executed_leak_rate.toFixed(2)}</td>
              <td>{group.mean_steps.toFixed(1)}</td>
              <td>{pct(group.stuck_rate)}</td>
              <td>
                {Math.round(group.latency_p50_ms)} /{" "}
                {Math.round(group.latency_p95_ms)} ms
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
