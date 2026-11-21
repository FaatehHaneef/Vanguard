"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { api, type EnforcementOption, type Persona, type Site, type Task } from "@/lib/api";
import { characterFor } from "@/lib/cast";
import { Sprite } from "./Sprite";

const OPTIONS: { id: EnforcementOption; label: string; help: string }[] = [
  {
    id: "prompt_only",
    label: "Prompt only",
    help: "The limits are only described to the model. The baseline.",
  },
  {
    id: "gate",
    label: "Gate",
    help: "Code refuses any action outside the limits before it reaches the page.",
  },
];

function newBatchId(): string {
  return Array.from(crypto.getRandomValues(new Uint8Array(8)), (b) =>
    b.toString(16).padStart(2, "0"),
  ).join("");
}

/** Step two of a trial: where the chosen party goes, with which task and settings. */
export function SitePicker() {
  const router = useRouter();
  const params = useSearchParams();
  const partyIds = useMemo(
    () => (params.get("party") ?? "").split(",").filter(Boolean),
    [params],
  );

  const [personas, setPersonas] = useState<Persona[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [providers, setProviders] = useState<string[]>([]);
  const [siteId, setSiteId] = useState("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [taskId, setTaskId] = useState("");
  const [option, setOption] = useState<EnforcementOption>("gate");
  const [provider, setProvider] = useState("");
  const [repeats, setRepeats] = useState(1);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.personas(), api.sites(), api.health()])
      .then(([allPersonas, allSites, health]) => {
        setPersonas(allPersonas.filter((persona) => partyIds.includes(persona.id)));
        setSites(allSites);
        setSiteId((current) => current || allSites[0]?.id || "");
        setProviders(health.providers);
        setProvider((current) => current || health.providers[0] || "");
      })
      .catch(() => setError("The Vanguard API is not reachable. Is the backend running?"));
  }, [partyIds]);

  useEffect(() => {
    if (!siteId) return;
    api
      .tasks(siteId)
      .then((found) => {
        setTasks(found);
        setTaskId(found[0]?.id ?? "");
      })
      .catch(() => setError("Could not load the tasks for this site."));
  }, [siteId]);

  async function start() {
    setStarting(true);
    setError("");
    const batch = newBatchId();
    try {
      for (const persona of personas) {
        // Preview personas only run with their limits described in the prompt.
        const enforcement: EnforcementOption[] =
          persona.status === "preview" ? ["prompt_only"] : [option];
        for (let repeat = 0; repeat < repeats; repeat++) {
          await api.startRun({
            site_id: siteId,
            task_id: taskId,
            persona_id: persona.id,
            enforcement,
            provider,
            repeat_index: repeat,
            batch_id: batch,
          });
        }
      }
      router.push(`/trials/${batch}`);
    } catch (problem) {
      setError(problem instanceof Error ? problem.message : "The trial could not start.");
      setStarting(false);
    }
  }

  if (partyIds.length === 0) {
    return (
      <p className="text-parchment">
        No one has been chosen yet.{" "}
        <Link href="/lobby" className="text-amber underline">
          Choose your simulated users
        </Link>
        .
      </p>
    );
  }

  const previews = personas.filter((persona) => persona.status === "preview");

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_22rem]">
      <div className="grid gap-6">
        <section className="pixel-panel" aria-labelledby="where">
          <h2 id="where" className="font-display text-2xl font-bold text-amber">
            Where
          </h2>
          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {sites.map((site) => (
              <label
                key={site.id}
                className={`pixel-panel flush cursor-pointer p-4 ${site.id === siteId ? "lit" : ""}`}
              >
                <input
                  type="radio"
                  name="site"
                  className="sr-only"
                  checked={site.id === siteId}
                  onChange={() => setSiteId(site.id)}
                />
                <span className="font-display text-xl font-bold text-parchment">{site.name}</span>
                <span className="mt-1 block text-sm text-mist">{site.description}</span>
              </label>
            ))}
            <div className="pixel-panel flush p-4 opacity-60">
              <span className="font-display text-xl font-bold text-parchment">Your own site</span>
              <span className="mt-1 block text-sm text-mist">Coming in the next phase.</span>
            </div>
          </div>
        </section>

        <section className="pixel-panel" aria-labelledby="task">
          <h2 id="task" className="font-display text-2xl font-bold text-amber">
            Task
          </h2>
          <div className="mt-3 grid gap-2">
            {tasks.map((task) => (
              <label key={task.id} className="flex cursor-pointer items-start gap-3">
                <input
                  type="radio"
                  name="task"
                  className="round-check mt-1"
                  checked={task.id === taskId}
                  onChange={() => setTaskId(task.id)}
                />
                <span className="text-parchment">{task.instruction}</span>
              </label>
            ))}
          </div>
        </section>

        <section className="pixel-panel" aria-labelledby="how">
          <h2 id="how" className="font-display text-2xl font-bold text-amber">
            How the limits are kept
          </h2>
          <div className="mt-3 grid gap-2">
            {OPTIONS.map((entry) => (
              <label key={entry.id} className="flex cursor-pointer items-start gap-3">
                <input
                  type="radio"
                  name="option"
                  className="round-check mt-1"
                  checked={entry.id === option}
                  onChange={() => setOption(entry.id)}
                />
                <span>
                  <span className="font-bold text-parchment">{entry.label}.</span>{" "}
                  <span className="text-mist">{entry.help}</span>
                </span>
              </label>
            ))}
          </div>
          {previews.length > 0 ? (
            <p className="mt-3 text-sm text-mist">
              {previews.map((persona) => persona.name).join(", ")}{" "}
              {previews.length === 1 ? "is a preview persona and runs" : "are preview personas and run"}{" "}
              prompt-only whatever you choose.
            </p>
          ) : null}
        </section>
      </div>

      <aside className="pixel-panel lit flex h-fit flex-col gap-4">
        <p className="font-display text-sm uppercase tracking-widest text-amber">Party</p>
        <div className="flex flex-wrap items-end gap-3">
          {personas.map((persona) => {
            const character = characterFor(persona.id);
            return character ? (
              <figure key={persona.id} className="flex flex-col items-center">
                <Sprite id={character.id} scale={3} />
                <figcaption className="font-display text-sm text-parchment">
                  {character.name}
                </figcaption>
              </figure>
            ) : null;
          })}
        </div>

        <label className="grid gap-1 text-parchment">
          Model
          <select
            className="rounded bg-night px-2 py-1 text-parchment"
            value={provider}
            onChange={(event) => setProvider(event.target.value)}
          >
            {providers.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>

        <label className="grid gap-1 text-parchment">
          Runs per persona
          <input
            type="number"
            min={1}
            max={5}
            value={repeats}
            onChange={(event) => setRepeats(Math.min(5, Math.max(1, Number(event.target.value))))}
            className="rounded bg-night px-2 py-1 text-parchment"
          />
        </label>

        <button
          type="button"
          className="pixel-button text-xl"
          onClick={start}
          disabled={starting || !siteId || !taskId || personas.length === 0}
        >
          {starting ? "Sending them in…" : "Start the trial"}
        </button>
        <Link href="/lobby" className="pixel-button quiet text-center">
          Change the party
        </Link>
        <p role="alert" className="font-bold text-rose">
          {error}
        </p>
      </aside>
    </div>
  );
}
