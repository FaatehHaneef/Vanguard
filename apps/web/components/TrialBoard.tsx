"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, type Persona, type RunSummary } from "@/lib/api";
import { characterFor } from "@/lib/cast";
import { Sprite } from "./Sprite";

const OUTCOME: Record<string, string> = {
  success: "Completed the task",
  gave_up: "Gave up",
  stuck: "Got stuck",
  step_limit: "Ran out of steps",
  error: "Run failed",
};

export function outcomeText(run: RunSummary): string {
  if (run.status === "queued") return "Waiting to start";
  if (run.status === "running") return "On the way…";
  return run.outcome ? OUTCOME[run.outcome] : run.status;
}

/** Every run in one trial (batch), refreshed until all have finished. */
export function TrialBoard() {
  const { batch: batchId } = useParams<{ batch: string }>();
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [personas, setPersonas] = useState<Record<string, Persona>>({});
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .personas()
      .then((all) => setPersonas(Object.fromEntries(all.map((persona) => [persona.id, persona]))))
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    let timer = 0;
    const load = async () => {
      try {
        const found = await api.runs(batchId);
        setRuns(found);
        if (found.some((run) => run.status === "queued" || run.status === "running")) {
          timer = window.setTimeout(load, 1500);
        }
      } catch {
        setError("The Vanguard API is not reachable.");
      }
    };
    void load();
    return () => window.clearTimeout(timer);
  }, [batchId]);

  if (error) return <p className="font-bold text-rose">{error}</p>;
  if (runs.length === 0) return <p className="text-mist">No runs in this trial yet.</p>;

  return (
    <ul className="grid gap-3 sm:grid-cols-2">
      {[...runs].reverse().map((run) => {
        const character = characterFor(run.config.persona_id);
        const persona = personas[run.config.persona_id];
        const done = run.status === "finished" || run.status === "failed";
        return (
          <li key={run.id}>
            <Link href={`/runs/${run.id}`} className="pixel-panel flex items-center gap-4 p-4">
              {character ? (
                <Sprite
                  id={character.id}
                  scale={3}
                  mood={!done ? "walk" : run.outcome === "success" ? "happy" : "worry"}
                />
              ) : null}
              <span className="grid gap-1">
                <span className="font-display text-xl font-bold text-parchment">
                  {character?.name ?? run.config.persona_id}
                  {persona?.status === "preview" ? (
                    <span className="preview-badge ml-2 align-middle">Preview</span>
                  ) : null}
                </span>
                <span className="text-parchment">{outcomeText(run)}</span>
                <span className="text-sm text-mist">
                  {run.config.enforcement.join(" + ")} · run {(run.config.repeat_index ?? 0) + 1}{" "}
                  · {run.steps} steps · {run.blocked} refused
                </span>
              </span>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
