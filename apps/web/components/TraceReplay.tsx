"use client";

import { useEffect, useState } from "react";
import {
  api,
  type Action,
  type RunReport,
  type Step,
  type Violation,
} from "@/lib/api";

const PLAY_MS = 1800;

function describe(action: Action): string {
  const args = Object.entries(action)
    .filter(
      ([key, value]) => key !== "tool" && key !== "rationale" && value != null,
    )
    .map(([key, value]) => `${key}=${JSON.stringify(value)}`);
  return `${action.tool}(${args.join(", ")})`;
}

function Decision({
  title,
  allowed,
  rule,
  message,
}: {
  title: string;
  allowed: boolean;
  rule: string | null;
  message: string | null;
}) {
  return (
    <div className="grid gap-1">
      <dt className="text-sm text-mist">{title}</dt>
      <dd className={allowed ? "text-moss" : "font-bold text-rose"}>
        {allowed ? "Allowed" : `Refused${rule ? ` (rule ${rule})` : ""}`}
        {message ? (
          <span className="block font-normal text-parchment">{message}</span>
        ) : null}
      </dd>
    </div>
  );
}

function Violations({ label, list }: { label: string; list: Violation[] }) {
  if (list.length === 0) return null;
  return (
    <div className="grid gap-1">
      <dt className="text-sm text-mist">{label}</dt>
      <dd>
        <ul className="grid gap-1">
          {list.map((v) => (
            <li key={`${v.rule}-${v.message}`} className="text-parchment">
              <span className="font-bold text-amber">
                {v.rule}
                {v.limit ? ` · ${v.limit}` : ""}
              </span>{" "}
              {v.message}
            </li>
          ))}
        </ul>
      </dd>
    </div>
  );
}

/**
 * Replay a run one step at a time: the screen the persona was on, what it perceived,
 * what it proposed and why, what the gate (and verifier) decided and why, what
 * happened in the page, and what the checker found. Arrow keys move between steps.
 */
export function TraceReplay({
  runId,
  steps,
  report,
}: {
  runId: string;
  steps: Step[];
  report: RunReport | null;
}) {
  const [at, setAt] = useState(0);
  const [playing, setPlaying] = useState(false);
  const last = steps.length - 1;
  const current = Math.min(at, Math.max(0, last));

  useEffect(() => {
    if (!playing || current >= last) return;
    const timer = window.setTimeout(() => {
      setAt(current + 1);
      if (current + 1 >= last) setPlaying(false);
    }, PLAY_MS);
    return () => window.clearTimeout(timer);
  }, [playing, current, last]);

  if (steps.length === 0) return null;
  const step = steps[current];
  const verdict = report?.steps.find((entry) => entry.index === step.index);
  const inCall = step.in_call ?? 0;
  const callSize = steps.filter(
    (s) => s.call != null && s.call === step.call,
  ).length;

  const go = (index: number) => {
    setPlaying(false);
    setAt(Math.max(0, Math.min(last, index)));
  };

  return (
    <section
      className="pixel-panel grid gap-4"
      aria-labelledby="replay-title"
      onKeyDown={(event) => {
        if (event.key === "ArrowRight") go(current + 1);
        if (event.key === "ArrowLeft") go(current - 1);
      }}
    >
      <div className="flex flex-wrap items-baseline justify-between gap-3">
        <h2
          id="replay-title"
          className="font-display text-xl font-bold text-amber"
        >
          Replay
        </h2>
        <p className="text-sm text-mist" aria-live="polite">
          Step {current + 1} of {steps.length}
          {step.call != null
            ? ` · model call ${step.call + 1}${callSize > 1 ? `, action ${inCall + 1} of ${callSize}` : ""}`
            : ""}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          className="pixel-button quiet"
          onClick={() => go(0)}
          disabled={current === 0}
        >
          First
        </button>
        <button
          type="button"
          className="pixel-button quiet"
          onClick={() => go(current - 1)}
          disabled={current === 0}
        >
          Previous
        </button>
        <button
          type="button"
          className="pixel-button"
          onClick={() => {
            if (current >= last) setAt(0);
            setPlaying(!playing);
          }}
        >
          {playing ? "Pause" : "Play"}
        </button>
        <button
          type="button"
          className="pixel-button quiet"
          onClick={() => go(current + 1)}
          disabled={current === last}
        >
          Next
        </button>
        <button
          type="button"
          className="pixel-button quiet"
          onClick={() => go(last)}
          disabled={current === last}
        >
          Last
        </button>
        <label className="flex flex-1 items-center gap-2 text-sm text-mist">
          <span className="sr-only">Step</span>
          <input
            type="range"
            min={0}
            max={last}
            value={current}
            onChange={(event) => go(Number(event.target.value))}
            className="w-full min-w-32 accent-amber"
          />
        </label>
      </div>

      <div className="grid gap-4 lg:grid-cols-[3fr_2fr]">
        <figure className="grid content-start gap-2">
          {step.observation.screenshot_path ? (
            /* eslint-disable-next-line @next/next/no-img-element -- served by the API */
            <img
              src={api.screenshotUrl(runId, step.index)}
              alt={`The screen before step ${step.index + 1}`}
              className="w-full rounded border border-line"
            />
          ) : (
            <p className="rounded border border-line p-6 text-mist">
              No screenshot for this step.
            </p>
          )}
          <figcaption className="break-all text-sm text-mist">
            {step.observation.url}
          </figcaption>
        </figure>

        <dl className="grid content-start gap-3">
          <div className="grid gap-1">
            <dt className="text-sm text-mist">Proposed</dt>
            <dd>
              <code className="text-parchment">
                {step.proposed ? describe(step.proposed) : "(no valid action)"}
              </code>
              {step.proposed?.rationale ? (
                <span className="block text-sm italic text-mist">
                  &ldquo;{step.proposed.rationale}&rdquo;
                </span>
              ) : null}
              {step.model_error ? (
                <span className="block text-sm text-rose">
                  {step.model_error}
                </span>
              ) : null}
            </dd>
          </div>
          <Decision
            title="Gate"
            allowed={step.gate.allowed}
            rule={step.gate.rule}
            message={step.gate.allowed ? null : step.gate.message}
          />
          {step.verifier ? (
            <Decision
              title="Verifier"
              allowed={step.verifier.allowed}
              rule={step.verifier.rule}
              message={step.verifier.message}
            />
          ) : null}
          <div className="grid gap-1">
            <dt className="text-sm text-mist">In the page</dt>
            <dd className="text-parchment">
              {step.executed
                ? step.execution_error
                  ? `Failed: ${step.execution_error}`
                  : `Done${step.url_after && step.url_after !== step.observation.url ? ` → ${step.url_after}` : ""}`
                : "Not carried out"}
              <span className="block text-sm text-mist">
                Input events:{" "}
                {step.events.map((e) => e.type).join(", ") || "none"} ·{" "}
                {Math.round(step.latency_ms)} ms
              </span>
            </dd>
          </div>
          {verdict ? (
            <>
              <Violations
                label="Broke a limit (checker)"
                list={verdict.executed}
              />
              <Violations
                label="Tried to break a limit (checker)"
                list={verdict.attempted.filter(
                  (a) => !verdict.executed.some((e) => e.rule === a.rule),
                )}
              />
              {verdict.attempted.length === 0 ? (
                <div className="grid gap-1">
                  <dt className="text-sm text-mist">Checker</dt>
                  <dd className="text-moss">
                    Within the persona&apos;s limits
                  </dd>
                </div>
              ) : null}
            </>
          ) : null}
          <details className="grid gap-1">
            <summary className="cursor-pointer text-sm text-mist">
              What the persona perceived
              {inCall > 0
                ? " (the page state; the model planned on its call's first step)"
                : ""}
            </summary>
            <pre className="mt-1 max-h-72 overflow-auto whitespace-pre-wrap rounded bg-night p-2 text-xs text-parchment">
              {step.observation.content}
            </pre>
          </details>
        </dl>
      </div>
    </section>
  );
}
