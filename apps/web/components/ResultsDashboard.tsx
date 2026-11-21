"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type BatchStatus, type FailureGroup } from "@/lib/api";
import { BatchMetrics } from "./BatchMetrics";

type Agreement = {
  overlap: number;
  kappa?: number;
  raw_agreement?: number;
  checker_vs_agreed?: {
    steps: number;
    kappa: number;
    precision: number;
    recall: number;
  };
  [key: string]: unknown;
};

function pct(value: number): string {
  return `${Math.round(value * 100)}%`;
}

function Failures({ batchId }: { batchId: string }) {
  const [groups, setGroups] = useState<FailureGroup[]>([]);
  useEffect(() => {
    let live = true;
    api.failures(batchId).then(
      (found) => live && setGroups(found),
      () => undefined,
    );
    return () => {
      live = false;
    };
  }, [batchId]);
  if (groups.length === 0) return null;
  const total = groups.reduce((sum, group) => sum + group.count, 0);
  return (
    <section className="pixel-panel grid gap-2" aria-label="Failures by cause">
      <h3 className="font-display text-lg font-bold text-amber">
        {total} failing runs, by cause
      </h3>
      <ul className="grid gap-1 text-sm text-parchment">
        {groups.map((group) => (
          <li key={group.cause}>
            <strong>{group.count}</strong> · {group.meaning}{" "}
            <span className="text-mist">
              (
              {group.runs.slice(0, 3).map((run, index) => (
                <span key={run.run_id}>
                  {index > 0 ? ", " : ""}
                  <Link href={`/runs/${run.run_id}`} className="underline">
                    {run.run_id.slice(0, 6)}
                  </Link>
                </span>
              ))}
              )
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function AgreementPanel() {
  const [people, setPeople] = useState<{ labeller: string; labels: number }[]>(
    [],
  );
  const [report, setReport] = useState<Agreement | null>(null);

  useEffect(() => {
    let live = true;
    api.labellers().then(
      (found) => {
        if (!live) return;
        setPeople(found);
        if (found.length >= 2) {
          api.agreement(found[0].labeller, found[1].labeller).then(
            (value) => live && setReport(value as Agreement),
            () => undefined,
          );
        }
      },
      () => undefined,
    );
    return () => {
      live = false;
    };
  }, []);

  return (
    <section
      className="pixel-panel grid gap-2"
      aria-labelledby="agreement-title"
    >
      <h2
        id="agreement-title"
        className="font-display text-xl font-bold text-amber"
      >
        Labels and agreement
      </h2>
      {people.length === 0 ? (
        <p className="text-mist">
          No labels yet. Start at the{" "}
          <Link href="/labelling" className="underline">
            labelling desk
          </Link>
          .
        </p>
      ) : (
        <p className="text-parchment">
          {people
            .map((person) => `${person.labeller}: ${person.labels}`)
            .join(" · ")}
        </p>
      )}
      {report && report.overlap > 0 ? (
        <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div>
            <dt className="text-sm text-mist">Steps both labelled</dt>
            <dd className="font-display text-lg text-parchment">
              {report.overlap}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-mist">Cohen&apos;s kappa</dt>
            <dd className="font-display text-lg text-parchment">
              {report.kappa?.toFixed(2) ?? "–"}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-mist">Raw agreement</dt>
            <dd className="font-display text-lg text-parchment">
              {report.raw_agreement !== undefined
                ? pct(report.raw_agreement)
                : "–"}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-mist">Checker vs agreed labels</dt>
            <dd className="font-display text-lg text-parchment">
              {report.checker_vs_agreed
                ? `κ ${report.checker_vs_agreed.kappa.toFixed(2)} · P ${pct(
                    report.checker_vs_agreed.precision,
                  )} · R ${pct(report.checker_vs_agreed.recall)}`
                : "–"}
            </dd>
          </div>
        </dl>
      ) : null}
    </section>
  );
}

/** Everything the evaluation needs on one page, computed by the backend's code. */
export function ResultsDashboard() {
  const [batches, setBatches] = useState<BatchStatus[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let live = true;
    api.batches().then(
      (found) => live && setBatches(found),
      () => live && setError("The Vanguard API is not reachable."),
    );
    return () => {
      live = false;
    };
  }, []);

  if (error) return <p className="font-bold text-rose">{error}</p>;

  return (
    <div className="grid gap-8">
      <AgreementPanel />
      {batches.length === 0 ? (
        <p className="text-mist">No batches yet.</p>
      ) : null}
      {batches.map((batch) => {
        const done = batch.groups.reduce((sum, group) => sum + group.done, 0);
        const target = batch.groups.reduce(
          (sum, group) => sum + group.target,
          0,
        );
        return (
          <article key={batch.batch_id} className="grid gap-3">
            <h2 className="font-display text-2xl font-bold text-parchment">
              <Link
                href={`/trials/${batch.batch_id}`}
                className="underline underline-offset-4"
              >
                Batch {batch.batch_id}
              </Link>
            </h2>
            <p className="text-mist">
              {done} of {target} runs finished
              {batch.stopped ? ` · stopped: ${batch.stopped}` : ""}
            </p>
            <BatchMetrics batchId={batch.batch_id} refreshKey={done} />
            <Failures batchId={batch.batch_id} />
          </article>
        );
      })}
    </div>
  );
}
