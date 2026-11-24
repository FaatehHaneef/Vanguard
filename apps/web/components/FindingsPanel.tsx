import type { Attribution, FindingKind, FindingsReport } from "@/lib/api";

const KIND: Record<FindingKind, string> = {
  inaccessible_control: "Inaccessible control",
  navigation_failure: "Navigation failure",
  repeated_actions: "Repeated actions",
  confusing_workflow: "Confusing workflow",
  failed_task: "Failed task",
};

export const ATTRIBUTION: Record<Attribution, string> = {
  site: "The site: the control agent fails this task too",
  restriction:
    "A barrier for this persona's limits: a candidate for evaluation by people",
  agent: "The simulated user itself: the control agent succeeds",
  infrastructure: "The model or the browser failed: nothing can be concluded",
  unknown: "Unknown: no control run of this task to compare with",
};

/** What the audit found in a run and why it failed. Computed by code, not a model. */
export function FindingsPanel({ report }: { report: FindingsReport }) {
  const why = report.attributions[0];
  return (
    <section
      className="pixel-panel grid gap-3"
      aria-labelledby="findings-title"
    >
      <h2
        id="findings-title"
        className="font-display text-xl font-bold text-amber"
      >
        Findings
      </h2>
      {why ? (
        <div className="grid gap-1">
          <p className="font-bold text-parchment">
            Why it failed: {ATTRIBUTION[why.attribution]}
          </p>
          <p className="text-sm text-mist">{why.reason}</p>
        </div>
      ) : null}
      {report.findings.length > 0 ? (
        <ul className="grid gap-2">
          {report.findings.map((finding, i) => (
            <li key={`${finding.kind}-${i}`} className="text-parchment">
              <span className="font-bold text-amber">{KIND[finding.kind]}</span>{" "}
              {finding.summary}
              {finding.steps.length > 0 ? (
                <span className="text-sm text-mist">
                  {" "}
                  (step {finding.steps.map((s) => s + 1).join(", ")})
                </span>
              ) : null}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-moss">No usability problems found in this run.</p>
      )}
      <p className="text-xs text-mist">{report.limits_statement}</p>
    </section>
  );
}
