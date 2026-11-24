"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  api,
  type Condition,
  type EnforcementOption,
  type Persona,
  type Site,
  type Task,
} from "@/lib/api";
import { castFor } from "@/lib/cast";
import { Sprite } from "./Sprite";

type Choice = "prompt_only" | "gate" | "verifier" | "bounded" | "compare";

const OPTIONS: {
  id: Choice;
  label: string;
  help: string;
  runs: EnforcementOption[][];
}[] = [
  {
    id: "compare",
    label: "Compare",
    help: "Runs every persona both ways, prompt only and with the gate, side by side.",
    runs: [["prompt_only"], ["gate"]],
  },
  {
    id: "prompt_only",
    label: "Prompt only",
    help: "The limits are only described to the model. The baseline.",
    runs: [["prompt_only"]],
  },
  {
    id: "gate",
    label: "Gate",
    help: "Code refuses any action outside the limits before it reaches the page.",
    runs: [["gate"]],
  },
  {
    id: "bounded",
    label: "Bounded perception",
    help: "Each persona perceives only what its user would, e.g. Echo hears the accessibility tree.",
    runs: [["bounded_perception"]],
  },
  {
    id: "verifier",
    label: "Verifier",
    help: "A second AI call checks each action against the limits before it runs.",
    runs: [["verifier"]],
  },
];

const CONDITIONS: { id: Condition; label: string }[] = [
  { id: "mobile", label: "On a phone (390 by 844, touch)" },
  { id: "slow_network", label: "On a slow connection (about 3G)" },
];

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
  const [option, setOption] = useState<Choice>("compare");
  const [conditions, setConditions] = useState<Condition[]>([]);
  const [provider, setProvider] = useState("");
  const [repeats, setRepeats] = useState(1);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.personas(), api.sites(), api.health()])
      .then(([allPersonas, allSites, health]) => {
        setPersonas(
          allPersonas.filter((persona) => partyIds.includes(persona.id)),
        );
        setSites(allSites);
        setSiteId((current) => current || allSites[0]?.id || "");
        setProviders(health.providers);
        setProvider((current) => current || health.providers[0] || "");
      })
      .catch(() =>
        setError("The Vanguard API is not reachable. Is the backend running?"),
      );
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
    try {
      // One balanced batch, run one at a time by the backend. Preview personas are
      // given prompt-only runs there, whatever is chosen here.
      const status = await api.startBatch({
        site_id: siteId,
        task_ids: [taskId],
        persona_ids: personas.map((persona) => persona.id),
        enforcements: OPTIONS.find((entry) => entry.id === option)?.runs ?? [
          ["gate"],
        ],
        conditions,
        provider,
        repeats,
      });
      router.push(`/trials/${status.batch_id}`);
    } catch (problem) {
      setError(
        problem instanceof Error
          ? problem.message
          : "The trial could not start.",
      );
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
                <span className="font-display text-xl font-bold text-parchment">
                  {site.name}
                </span>
                <span className="mt-1 block text-sm text-mist">
                  {site.description}
                </span>
              </label>
            ))}
            <Link
              href="/studio/sites"
              className="pixel-panel flush block p-4 hover:border-amber"
            >
              <span className="font-display text-xl font-bold text-parchment">
                Your own site
              </span>
              <span className="mt-1 block text-sm text-mist">
                Add any website and its tasks in the studio. It appears here
                once saved.
              </span>
            </Link>
          </div>
        </section>

        <section className="pixel-panel" aria-labelledby="task">
          <h2 id="task" className="font-display text-2xl font-bold text-amber">
            Task
          </h2>
          <div className="mt-3 grid gap-2">
            {tasks.map((task) => (
              <label
                key={task.id}
                className="flex cursor-pointer items-start gap-3"
              >
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
              <label
                key={entry.id}
                className="flex cursor-pointer items-start gap-3"
              >
                <input
                  type="radio"
                  name="option"
                  className="round-check mt-1"
                  checked={entry.id === option}
                  onChange={() => setOption(entry.id)}
                />
                <span>
                  <span className="font-bold text-parchment">
                    {entry.label}.
                  </span>{" "}
                  <span className="text-mist">{entry.help}</span>
                </span>
              </label>
            ))}
          </div>
          <fieldset className="mt-4 grid gap-2">
            <legend className="font-bold text-parchment">
              Conditions (optional)
            </legend>
            {CONDITIONS.map((entry) => (
              <label
                key={entry.id}
                className="flex cursor-pointer items-center gap-3"
              >
                <input
                  type="checkbox"
                  checked={conditions.includes(entry.id)}
                  onChange={(event) =>
                    setConditions((current) =>
                      event.target.checked
                        ? [...current, entry.id]
                        : current.filter((id) => id !== entry.id),
                    )
                  }
                />
                <span className="text-mist">{entry.label}</span>
              </label>
            ))}
          </fieldset>
          {previews.length > 0 ? (
            <p className="mt-3 text-sm text-mist">
              {previews.map((persona) => persona.name).join(", ")}{" "}
              {previews.length === 1
                ? "is a preview persona and runs"
                : "are preview personas and run"}{" "}
              prompt-only whatever you choose.
            </p>
          ) : null}
        </section>
      </div>

      <aside className="pixel-panel lit flex h-fit flex-col gap-4">
        <p className="font-display text-sm uppercase tracking-widest text-amber">
          Party
        </p>
        <div className="flex flex-wrap items-end gap-3">
          {personas.map((persona) => {
            const character = castFor(persona);
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
            onChange={(event) =>
              setRepeats(Math.min(5, Math.max(1, Number(event.target.value))))
            }
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
