"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { api, type BatchStatus } from "@/lib/api";
import {
  type CompareGroup,
  type Comparison,
  describeKey,
  fetchComparison,
  type Match,
  type Verdict,
} from "./client";
import { FailureChanges } from "./FailureChanges";

const VERDICT_TEXT: Record<Verdict, string> = {
  better: "Better",
  worse: "Worse",
  same: "Same",
  only_baseline: "Only in the baseline",
  only_candidate: "Only in the candidate",
};

const VERDICT_STYLE: Record<Verdict, string> = {
  better: "border-moss text-moss",
  worse: "border-rose text-rose",
  same: "border-mist text-mist",
  only_baseline: "border-mist text-mist",
  only_candidate: "border-mist text-mist",
};

const ARROW: Record<Verdict, string> = {
  better: "▲",
  worse: "▼",
  same: "=",
  only_baseline: "",
  only_candidate: "",
};

type Column = {
  metric: string;
  label: string;
  format: (value: number) => string;
  /** For values the API does not judge (failures): lower is better. */
  lowerIsBetter?: boolean;
};

const percent = (value: number) => `${Math.round(value * 100)}%`;
const decimal = (value: number) => value.toFixed(1);

const COLUMNS: Column[] = [
  { metric: "success_rate", label: "Success", format: percent },
  { metric: "any_leak_rate", label: "Runs with a leak", format: percent },
  { metric: "mean_steps", label: "Steps (mean)", format: decimal },
  { metric: "mean_repeated_attempts", label: "Repeated attempts (mean)", format: decimal },
  { metric: "failures", label: "Failures", format: String, lowerIsBetter: true },
];

export function VerdictBadge({ verdict }: { verdict: Verdict }) {
  return (
    <span className={`inline-block whitespace-nowrap rounded border-2 px-2 py-0.5 text-sm font-bold ${VERDICT_STYLE[verdict]}`}>
      {ARROW[verdict] ? <span aria-hidden="true">{ARROW[verdict]} </span> : null}
      {VERDICT_TEXT[verdict]}
    </span>
  );
}

function cell(group: CompareGroup, column: Column) {
  const before = group.baseline?.[column.metric as keyof typeof group.baseline] as number | undefined;
  const after = group.candidate?.[column.metric as keyof typeof group.candidate] as number | undefined;
  const change = group.changes.find((item) => item.metric === column.metric);
  let verdict: Verdict | null = change?.verdict ?? null;
  if (!verdict && column.lowerIsBetter && before !== undefined && after !== undefined)
    verdict = after < before ? "better" : after > before ? "worse" : "same";
  return { before, after, verdict };
}

function GroupRow({ group, names, columns }: { group: CompareGroup; names: Record<string, string>; columns: Column[] }) {
  const parts = describeKey(group.key, names);
  return (
    <tr className="border-t-2 border-slate align-top">
      <th scope="row" className="py-3 pr-4 text-left font-normal">
        <span className="block font-bold text-parchment">{parts.persona}</span>
        <span className="block text-sm text-mist">
          {parts.task}
          {parts.method ? ` · ${parts.method}` : ""}
          {parts.provider ? ` · ${parts.provider}` : ""}
        </span>
        <span className="block text-xs text-mist">
          {group.baseline?.runs ?? 0} → {group.candidate?.runs ?? 0} runs
        </span>
      </th>
      {columns.map((column) => {
        const { before, after, verdict } = cell(group, column);
        return (
          <td key={column.metric} className="py-3 pr-4">
            <span className="block whitespace-nowrap text-parchment">
              {before === undefined ? "–" : column.format(before)} →{" "}
              {after === undefined ? "–" : column.format(after)}
            </span>
            {verdict && verdict !== "same" ? (
              <span className={`text-sm font-bold ${verdict === "better" ? "text-moss" : "text-rose"}`}>
                <span aria-hidden="true">{ARROW[verdict]} </span>
                {VERDICT_TEXT[verdict]}
              </span>
            ) : null}
          </td>
        );
      })}
      <td className="py-3">
        <VerdictBadge verdict={group.verdict} />
      </td>
    </tr>
  );
}

/**
 * Two batches side by side: choose a baseline and a candidate, and see per
 * persona/task/method group what got better, what got worse and what stayed the same.
 * The choice is kept in the address, so a comparison can be shared as a link.
 */
export function ComparisonReport() {
  const params = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  // The choice lives here and is copied to the address (for sharing), so two quick
  // changes never undo each other while the address is still updating.
  const [choice, setChoice] = useState(() => ({
    baseline: params.get("baseline") ?? "",
    candidate: params.get("candidate") ?? "",
    match: (params.get("match") === "persona_task" ? "persona_task" : "full") as Match,
  }));
  const { baseline, candidate, match } = choice;

  const [batches, setBatches] = useState<BatchStatus[] | null>(null);
  const [names, setNames] = useState<Record<string, string>>({});
  const [result, setResult] = useState<{ key: string; comparison?: Comparison; error?: string } | null>(null);
  const [problem, setProblem] = useState("");

  useEffect(() => {
    api
      .batches()
      .then(setBatches)
      .catch(() => setProblem("The Vanguard API is not reachable. Is the backend running?"));
    api
      .personas()
      .then((personas) => setNames(Object.fromEntries(personas.map((p) => [p.id, p.name]))))
      .catch(() => undefined);
  }, []);

  const wanted = baseline && candidate && baseline !== candidate ? `${baseline}|${candidate}|${match}` : "";
  useEffect(() => {
    if (!wanted) return;
    let current = true;
    fetchComparison(baseline, candidate, match)
      .then((comparison) => current && setResult({ key: wanted, comparison }))
      .catch((error: Error) => current && setResult({ key: wanted, error: error.message }));
    return () => {
      current = false;
    };
  }, [wanted, baseline, candidate, match]);

  const choose = (changes: Partial<typeof choice>) => {
    const next = { ...choice, ...changes };
    setChoice(next);
    const query = new URLSearchParams(Object.entries(next).filter(([, value]) => value));
    router.replace(`${pathname}?${query}`, { scroll: false });
  };

  const comparison = result?.key === wanted ? result.comparison : undefined;
  const error = result?.key === wanted ? result.error : undefined;
  const loading = Boolean(wanted) && result?.key !== wanted;

  const columns = useMemo(
    () =>
      COLUMNS.filter(
        (column) =>
          column.metric !== "mean_repeated_attempts" ||
          comparison?.groups.some(
            (group) =>
              group.baseline?.mean_repeated_attempts !== undefined ||
              group.candidate?.mean_repeated_attempts !== undefined,
          ),
      ),
    [comparison],
  );

  const counts = useMemo(() => {
    const found: Partial<Record<Verdict, number>> = {};
    for (const group of comparison?.groups ?? []) found[group.verdict] = (found[group.verdict] ?? 0) + 1;
    return found;
  }, [comparison]);

  const select = "w-full rounded border-2 border-slate bg-night px-3 py-2 text-parchment focus:border-amber";

  return (
    <div className="grid gap-6">
      <form className="pixel-panel grid gap-4 md:grid-cols-3" onSubmit={(event) => event.preventDefault()}>
        <label className="grid gap-1">
          <span className="font-bold text-parchment">Baseline (before)</span>
          <select className={select} value={baseline} onChange={(event) => choose({ baseline: event.target.value })}>
            <option value="">Choose a batch…</option>
            {batches?.map((batch) => (
              <option key={batch.batch_id} value={batch.batch_id}>
                {batch.batch_id}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1">
          <span className="font-bold text-parchment">Candidate (after)</span>
          <select className={select} value={candidate} onChange={(event) => choose({ candidate: event.target.value })}>
            <option value="">Choose a batch…</option>
            {batches?.map((batch) => (
              <option key={batch.batch_id} value={batch.batch_id}>
                {batch.batch_id}
              </option>
            ))}
          </select>
        </label>
        <label className="grid gap-1">
          <span className="font-bold text-parchment">Match groups on</span>
          <select className={select} value={match} onChange={(event) => choose({ match: event.target.value as Match })}>
            <option value="full">The same setup (persona, task, method, model)</option>
            <option value="persona_task">Persona and task only (compare methods or models)</option>
          </select>
        </label>
        <p className="text-sm text-mist md:col-span-3">
          Use the same setup to see whether a site change introduced new problems. Use persona and
          task only to compare enforcement methods or models on the same work.
        </p>
      </form>

      {problem ? <p role="alert" className="pixel-panel text-rose">{problem}</p> : null}
      {batches && batches.length < 2 ? (
        <p className="pixel-panel text-mist">You need at least two batches. Run a trial twice, for example before and after a site change.</p>
      ) : null}
      {baseline && candidate && baseline === candidate ? (
        <p className="pixel-panel text-mist">Choose two different batches.</p>
      ) : null}
      {loading ? <p className="text-mist">Comparing…</p> : null}
      {error ? <p role="alert" className="pixel-panel text-rose">{error}</p> : null}

      {comparison ? (
        <section aria-labelledby="groups-title" className="pixel-panel">
          <h2 id="groups-title" className="mb-2 font-display text-3xl font-bold text-amber">
            Group by group
          </h2>
          <p className="mb-4 text-parchment" role="status">
            {comparison.groups.length} groups: {counts.better ?? 0} better, {counts.worse ?? 0} worse,{" "}
            {counts.same ?? 0} the same
            {(counts.only_baseline ?? 0) + (counts.only_candidate ?? 0)
              ? `, ${(counts.only_baseline ?? 0) + (counts.only_candidate ?? 0)} in one batch only`
              : ""}
            .
          </p>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[46rem] border-collapse">
              <caption className="sr-only">
                Baseline {comparison.baseline} against candidate {comparison.candidate}, each value
                shown as before → after
              </caption>
              <thead>
                <tr className="text-left text-sm text-mist">
                  <th scope="col" className="pb-2 pr-4">Group</th>
                  {columns.map((column) => (
                    <th scope="col" key={column.metric} className="pb-2 pr-4">
                      {column.label}
                    </th>
                  ))}
                  <th scope="col" className="pb-2">Overall</th>
                </tr>
              </thead>
              <tbody>
                {comparison.groups.map((group) => (
                  <GroupRow key={group.key} group={group} names={names} columns={columns} />
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-4 text-sm text-mist">
            Higher success is better; fewer leaks, steps, repeated attempts and failures are
            better. A group is worse if any of its measures got worse. Measures come from the
            backend&rsquo;s checker, never from a model.
          </p>
        </section>
      ) : null}

      {comparison ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <FailureChanges
            tone="new"
            title="New failures"
            intro="Failure causes a group has in the candidate but not in the baseline: what the change may have broken."
            empty="No new failures: nothing failed in the candidate that did not already fail before."
            items={comparison.new_failures}
            names={names}
          />
          <FailureChanges
            tone="resolved"
            title="Resolved failures"
            intro="Failure causes a group had in the baseline that are gone from the candidate."
            empty="No failures were resolved."
            items={comparison.resolved_failures}
            names={names}
          />
        </div>
      ) : null}
    </div>
  );
}
