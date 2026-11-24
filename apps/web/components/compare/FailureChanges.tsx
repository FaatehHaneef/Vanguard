import Link from "next/link";
import { describeKey, type FailureChange } from "./client";

/** Failure causes that appear in only one batch, each with links to its runs. */
export function FailureChanges({
  title,
  intro,
  empty,
  items,
  names,
  tone,
}: {
  title: string;
  intro: string;
  empty: string;
  items: FailureChange[];
  names: Record<string, string>;
  tone: "new" | "resolved";
}) {
  const id = `failures-${tone}`;
  return (
    <section aria-labelledby={id} className={`pixel-panel ${tone === "new" && items.length ? "lit" : ""}`}>
      <h2 id={id} className={`mb-1 font-display text-3xl font-bold ${tone === "new" ? "text-rose" : "text-moss"}`}>
        {title} <span className="font-sans text-xl text-parchment">({items.length})</span>
      </h2>
      <p className="mb-4 text-mist">{intro}</p>
      {items.length ? (
        <ul className="grid gap-4">
          {items.map((item) => {
            const parts = describeKey(item.key, names);
            return (
              <li key={`${item.key}-${item.cause}`} className="border-l-4 border-slate pl-4">
                <p className="font-bold text-parchment">
                  {item.meaning}{" "}
                  <code className="text-xs font-normal text-mist">{item.cause}</code>
                </p>
                <p className="text-sm text-mist">
                  {parts.persona} · {parts.task}
                  {parts.method ? ` · ${parts.method}` : ""}
                  {parts.provider ? ` · ${parts.provider}` : ""}
                </p>
                <ul className="mt-1 flex flex-wrap gap-2" aria-label="Runs">
                  {item.run_ids.map((runId, index) => (
                    <li key={runId}>
                      <Link href={`/runs/${encodeURIComponent(runId)}`} className="text-amber underline">
                        Run {index + 1}
                        <span className="sr-only"> of {item.meaning.toLowerCase()}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </li>
            );
          })}
        </ul>
      ) : (
        <p className="text-parchment">{empty}</p>
      )}
    </section>
  );
}
