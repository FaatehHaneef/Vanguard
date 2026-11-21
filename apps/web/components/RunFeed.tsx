"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, type Action, type Persona, type RunSummary, type Step } from "@/lib/api";
import { characterFor } from "@/lib/cast";
import { Sprite } from "./Sprite";
import { outcomeText } from "./TrialBoard";

function describe(action: Action): string {
  const args = Object.entries(action)
    .filter(([key, value]) => key !== "tool" && key !== "rationale" && value != null)
    .map(([key, value]) => `${key}=${JSON.stringify(value)}`);
  return `${action.tool}(${args.join(", ")})`;
}

/** One run, step by step: what the persona perceived, proposed, and what the gate decided. */
export function RunFeed() {
  const { id: runId } = useParams<{ id: string }>();
  const [run, setRun] = useState<RunSummary | null>(null);
  const [steps, setSteps] = useState<Step[]>([]);
  const [persona, setPersona] = useState<Persona | null>(null);
  const [open, setOpen] = useState<number | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let timer = 0;
    const load = async () => {
      try {
        const [summary, found] = await Promise.all([api.run(runId), api.steps(runId)]);
        setRun(summary);
        setSteps(found);
        if (summary.status === "queued" || summary.status === "running") {
          timer = window.setTimeout(load, 1000);
        }
      } catch {
        setError("This run could not be loaded.");
      }
    };
    void load();
    return () => window.clearTimeout(timer);
  }, [runId]);

  useEffect(() => {
    if (!run) return;
    api
      .personas()
      .then((all) => setPersona(all.find((entry) => entry.id === run.config.persona_id) ?? null))
      .catch(() => undefined);
  }, [run]);

  if (error) return <p className="font-bold text-rose">{error}</p>;
  if (!run) return <p className="text-mist">Loading…</p>;

  const character = characterFor(run.config.persona_id);
  const done = run.status === "finished" || run.status === "failed";

  return (
    <div className="grid gap-6">
      <header className="pixel-panel lit flex flex-wrap items-center gap-6">
        {character ? (
          <Sprite
            id={character.id}
            scale={5}
            mood={!done ? "walk" : run.outcome === "success" ? "happy" : "worry"}
          />
        ) : null}
        <div className="grid gap-1">
          <p className="font-display text-3xl font-bold text-parchment">
            {character?.name ?? run.config.persona_id}
            {persona?.status === "preview" ? (
              <span className="preview-badge ml-3 align-middle">Preview</span>
            ) : null}
          </p>
          <p className="text-xl text-parchment">{outcomeText(run)}</p>
          <p className="text-mist">
            {run.config.task_id} on {run.config.site_id} · {run.config.enforcement.join(" + ")} ·{" "}
            {run.steps} steps · {run.blocked} refused
          </p>
          {run.error ? <p className="font-bold text-rose">{run.error}</p> : null}
          {persona?.status === "preview" ? (
            <p className="text-sm text-mist">
              Preview persona: limits were only described to the model. These results are not
              validated.
            </p>
          ) : null}
        </div>
      </header>

      <ol className="grid gap-2" aria-live="polite">
        {steps.map((step) => {
          const refused = !step.gate.allowed;
          return (
            <li key={step.index} className={`pixel-panel p-3 ${refused ? "step-refused" : ""}`}>
              <button
                type="button"
                className="flex w-full flex-wrap items-baseline gap-x-3 text-left"
                aria-expanded={open === step.index}
                onClick={() => setOpen(open === step.index ? null : step.index)}
              >
                <span className="font-display text-amber">{step.index + 1}</span>
                <code className="text-parchment">
                  {step.proposed ? describe(step.proposed) : "(no valid action)"}
                </code>
                <span className={refused ? "font-bold text-rose" : "text-moss"}>
                  {refused ? `Refused ${step.gate.rule ?? ""}` : step.executed ? "Done" : "Ended"}
                </span>
              </button>
              {step.proposed?.rationale ? (
                <p className="mt-1 text-sm italic text-mist">&ldquo;{step.proposed.rationale}&rdquo;</p>
              ) : null}
              {refused && step.gate.message ? (
                <p className="mt-1 text-sm text-rose">{step.gate.message}</p>
              ) : null}
              {open === step.index ? (
                <div className="mt-3 grid gap-2 text-sm">
                  <p className="text-mist">Perceived at {step.observation.url}:</p>
                  <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded bg-night p-2 text-parchment">
                    {step.observation.content}
                  </pre>
                  <p className="text-mist">
                    Input events: {step.events.map((event) => event.type).join(", ") || "none"} ·{" "}
                    {Math.round(step.latency_ms)} ms
                  </p>
                </div>
              ) : null}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
