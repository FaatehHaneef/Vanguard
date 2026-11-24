"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Sprite } from "@/components/Sprite";
import { isCustom, LIMITS, type PersonaSpec, studio, StudioError } from "@/lib/studio";

function limitNames(persona: PersonaSpec) {
  if (!persona.limits.length) return ["No limits"];
  return persona.limits.map((id) => LIMITS.find((limit) => limit.id === id)?.name ?? id);
}

function PersonaCard({
  persona,
  onDelete,
}: {
  persona: PersonaSpec;
  onDelete?: () => void;
}) {
  const custom = isCustom(persona.id);
  const [confirming, setConfirming] = useState(false);
  return (
    <li className={`pixel-panel flex flex-col gap-3 ${custom ? "lit" : ""}`}>
      <div className="flex items-start gap-4">
        <Sprite id={persona.character} scale={3} />
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-2xl font-bold text-parchment">
            {persona.name}{" "}
            {persona.status === "preview" ? (
              <span className="preview-badge align-middle">Preview</span>
            ) : null}
          </h3>
          <p className="text-mist">{persona.represents}</p>
        </div>
      </div>
      <ul className="flex flex-wrap gap-2" aria-label="Limits">
        {limitNames(persona).map((name) => (
          <li key={name} className="rounded bg-night px-2 py-0.5 text-sm text-parchment">
            {name}
          </li>
        ))}
      </ul>
      <p className="text-sm text-mist">
        {custom ? "Your persona" : "Built in, read-only"} · <code className="text-xs">{persona.id}</code>
      </p>
      <div className="mt-auto flex flex-wrap gap-2">
        <Link
          href={`/studio/personas/new?from=${encodeURIComponent(persona.id)}`}
          className={custom ? "pixel-button quiet" : "pixel-button"}
          aria-label={`Duplicate ${persona.name}`}
        >
          Duplicate
        </Link>
        {custom ? (
          <>
            <Link href={`/studio/personas/${encodeURIComponent(persona.id)}`} className="pixel-button">
              Edit
            </Link>
            <Link
              href={`/sites?party=${encodeURIComponent(persona.id)}`}
              className="pixel-button quiet"
            >
              Send on a trial
            </Link>
            {confirming ? (
              <span className="flex items-center gap-2" role="group" aria-label={`Delete ${persona.name}?`}>
                <button type="button" className="pixel-button quiet" onClick={onDelete}>
                  Yes, delete
                </button>
                <button type="button" className="pixel-button quiet" onClick={() => setConfirming(false)}>
                  Keep
                </button>
              </span>
            ) : (
              <button type="button" className="pixel-button quiet" onClick={() => setConfirming(true)}>
                Delete
              </button>
            )}
          </>
        ) : null}
      </div>
    </li>
  );
}

/** Every persona: the built-in cast (read-only) and the ones made in the studio. */
export function PersonaList() {
  const [personas, setPersonas] = useState<PersonaSpec[] | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    studio
      .allPersonas()
      .then(setPersonas)
      .catch((problem: Error) => setError(problem.message));
  }, []);

  async function remove(persona: PersonaSpec) {
    try {
      await studio.deletePersona(persona.id);
      setPersonas((current) => current?.filter((item) => item.id !== persona.id) ?? null);
      setNotice(`${persona.name} was deleted.`);
    } catch (problem) {
      setError(problem instanceof StudioError ? problem.message : "The persona could not be deleted.");
    }
  }

  if (error) return <p role="alert" className="pixel-panel text-rose">{error}</p>;
  if (!personas) return <p className="text-mist">Loading personas…</p>;

  const custom = personas.filter((persona) => isCustom(persona.id));
  const builtin = personas.filter((persona) => !isCustom(persona.id));

  return (
    <div className="grid gap-8">
      <p role="status" className="text-moss">
        {notice}
      </p>
      <section aria-labelledby="yours">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 id="yours" className="font-display text-3xl font-bold text-amber">
            Your personas
          </h2>
          <Link href="/studio/personas/new" className="pixel-button">
            New persona
          </Link>
        </div>
        {custom.length ? (
          <ul className="grid gap-5 md:grid-cols-2">
            {custom.map((persona) => (
              <PersonaCard key={persona.id} persona={persona} onDelete={() => remove(persona)} />
            ))}
          </ul>
        ) : (
          <p className="pixel-panel text-mist">
            You have not made a persona yet. Start from scratch, or duplicate one of the built-in
            cast below and change what you need.
          </p>
        )}
      </section>
      <section aria-labelledby="cast">
        <h2 id="cast" className="mb-4 font-display text-3xl font-bold text-amber">
          The built-in cast
        </h2>
        <ul className="grid gap-5 md:grid-cols-2">
          {builtin.map((persona) => (
            <PersonaCard key={persona.id} persona={persona} />
          ))}
        </ul>
      </section>
    </div>
  );
}
