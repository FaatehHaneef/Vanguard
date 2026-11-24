"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useEffect, useState } from "react";
import { Sprite } from "@/components/Sprite";
import { getCharacter } from "@/lib/cast";
import {
  CHARACTERS,
  expectedStatus,
  LIMITS,
  PERCEPTIONS,
  type PersonaDraft,
  type PersonaSpec,
  studio,
  StudioError,
  TOOL_GROUPS,
} from "@/lib/studio";
import { Choice, Field, FieldError, INPUT, ListField } from "./fields";

const BLANK: PersonaDraft = {
  name: "",
  character: "knock",
  represents: "",
  description: "",
  limits: [],
  perception: "full",
  tool_groups: ["keyboard", "pointer", "navigation", "control"],
  knowledge: { knows: ["general web conventions"], does_not_know: [] },
  magnification: null,
};

function draftOf(persona: PersonaSpec): PersonaDraft {
  return {
    name: persona.name,
    character: persona.character,
    represents: persona.represents,
    description: persona.description,
    limits: [...persona.limits],
    perception: persona.perception,
    tool_groups: [...persona.tool_groups],
    knowledge: {
      knows: [...persona.knowledge.knows],
      does_not_know: [...persona.knowledge.does_not_know],
    },
    magnification: persona.magnification,
  };
}

/** Combinations that make the persona contradict its own limits. Advice only. */
function warnings(draft: PersonaDraft): string[] {
  const found: string[] = [];
  const has = (limit: string) => draft.limits.includes(limit as never);
  if (has("L1") && draft.tool_groups.includes("pointer"))
    found.push("It has no pointer (L1) but may use pointer actions. Untick Pointer.");
  if (has("L2") && draft.perception !== "accessibility_tree")
    found.push("It perceives only the accessibility tree (L2), so choose that perception.");
  if (has("L3") && draft.perception !== "magnified")
    found.push("It sees a magnified view (L3), so choose the magnified window.");
  if (!draft.tool_groups.includes("control"))
    found.push("Without Control it can never finish a task or give up.");
  return found;
}

function toggle<T>(list: T[], item: T): T[] {
  return list.includes(item) ? list.filter((entry) => entry !== item) : [...list, item];
}

/**
 * Create a persona, edit one (personaId), or start from a copy of another (fromId).
 * Built-in personas can only be copied.
 */
export function PersonaEditor({ personaId, fromId }: { personaId?: string; fromId?: string }) {
  const router = useRouter();
  const [draft, setDraft] = useState<PersonaDraft | null>(personaId || fromId ? null : BLANK);
  const [all, setAll] = useState<PersonaSpec[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [problem, setProblem] = useState("");
  const [saving, setSaving] = useState(false);
  const [copiedFrom, setCopiedFrom] = useState("");

  useEffect(() => {
    studio
      .allPersonas()
      .then(setAll)
      .catch(() => undefined);
    const source = personaId ?? fromId;
    if (!source) return;
    studio
      .persona(source)
      .then((persona) => {
        if (fromId) {
          setCopiedFrom(persona.name);
          setDraft({ ...draftOf(persona), name: `${persona.name} (copy)` });
        } else {
          setDraft(draftOf(persona));
        }
      })
      .catch((error: Error) => setProblem(error.message));
  }, [personaId, fromId]);

  if (problem && !draft) return <p role="alert" className="pixel-panel text-rose">{problem}</p>;
  if (!draft) return <p className="text-mist">Loading…</p>;

  const update = (changes: Partial<PersonaDraft>) => setDraft({ ...draft, ...changes });
  const status = expectedStatus(draft, all);
  const advice = warnings(draft);
  const character = getCharacter(draft.character);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (!draft) return;
    setSaving(true);
    setErrors({});
    setProblem("");
    const body: PersonaDraft = {
      ...draft,
      magnification: draft.perception === "magnified" ? draft.magnification : null,
    };
    try {
      if (personaId) await studio.updatePersona(personaId, body);
      else await studio.createPersona(body);
      router.push("/studio/personas");
    } catch (error) {
      if (error instanceof StudioError) {
        setErrors(error.fields);
        setProblem(error.message);
      } else {
        setProblem("The persona could not be saved.");
      }
      setSaving(false);
    }
  }

  async function remove() {
    if (!personaId) return;
    try {
      await studio.deletePersona(personaId);
      router.push("/studio/personas");
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "The persona could not be deleted.");
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_22rem]">
      <form className="pixel-panel grid gap-6" onSubmit={save} noValidate>
        {copiedFrom ? (
          <p className="text-moss">
            A copy of {copiedFrom}. Change what you need, then save it as your own persona.
          </p>
        ) : null}

        <Field label="Name" hint="What the persona is called in the lobby and the results." error={errors.name}>
          {(props) => (
            <input
              {...props}
              className={INPUT}
              value={draft.name}
              onChange={(event) => update({ name: event.target.value })}
            />
          )}
        </Field>

        <fieldset className="grid gap-2">
          <legend className="font-bold text-parchment">Character</legend>
          <p className="text-sm text-mist">The sprite that walks the site for this persona.</p>
          <div className="flex flex-wrap gap-3">
            {CHARACTERS.map((id) => (
              <label
                key={id}
                className={`pixel-panel flush flex cursor-pointer flex-col items-center gap-1 p-3 has-[:focus-visible]:outline has-[:focus-visible]:outline-3 has-[:focus-visible]:outline-amber ${draft.character === id ? "lit" : ""}`}
              >
                <input
                  type="radio"
                  name="character"
                  className="sr-only"
                  checked={draft.character === id}
                  onChange={() => update({ character: id })}
                />
                <Sprite id={id} scale={2} />
                <span className="font-display text-parchment">{getCharacter(id).name}</span>
              </label>
            ))}
          </div>
          <FieldError error={errors.character} />
        </fieldset>

        <Field
          label="Represents"
          hint="One line: the kind of person this persona stands for."
          error={errors.represents}
        >
          {(props) => (
            <input
              {...props}
              className={INPUT}
              value={draft.represents}
              placeholder="A shopper who uses only a keyboard"
              onChange={(event) => update({ represents: event.target.value })}
            />
          )}
        </Field>

        <Field
          label="Description"
          hint="What the model is told about itself, in the second person. Say what it cannot do and how it gets around."
          error={errors.description}
        >
          {(props) => (
            <textarea
              {...props}
              rows={5}
              className={INPUT}
              value={draft.description}
              placeholder="You are a shopper who…"
              onChange={(event) => update({ description: event.target.value })}
            />
          )}
        </Field>

        <fieldset className="grid gap-3">
          <legend className="font-bold text-parchment">Limits</legend>
          <p className="text-sm text-mist">
            The limits are defined in the leakage specification. Vanguard checks every step against
            the limits you tick here.
          </p>
          {LIMITS.map((limit) => (
            <Choice
              key={limit.id}
              type="checkbox"
              title={`${limit.id} ${limit.name}`}
              meaning={limit.meaning}
              checked={draft.limits.includes(limit.id)}
              onChange={() => update({ limits: toggle(draft.limits, limit.id) })}
            />
          ))}
          <FieldError error={errors.limits} />
        </fieldset>

        <fieldset className="grid gap-3">
          <legend className="font-bold text-parchment">Perception</legend>
          <p className="text-sm text-mist">What the model is given of each page.</p>
          {PERCEPTIONS.map((perception) => (
            <Choice
              key={perception.id}
              type="radio"
              name="perception"
              title={perception.name}
              meaning={perception.meaning}
              checked={draft.perception === perception.id}
              onChange={() =>
                update({
                  perception: perception.id,
                  magnification: perception.id === "magnified" ? (draft.magnification ?? 4) : null,
                })
              }
            />
          ))}
          <FieldError error={errors.perception} />
        </fieldset>

        {draft.perception === "magnified" ? (
          <Field
            label="Magnification"
            hint="How many times the page is enlarged. At 4, a quarter of the width and height is visible."
            error={errors.magnification}
          >
            {(props) => (
              <input
                {...props}
                type="number"
                min={1.5}
                max={10}
                step={0.5}
                className={`${INPUT} max-w-32`}
                value={draft.magnification ?? ""}
                onChange={(event) =>
                  update({ magnification: event.target.value ? Number(event.target.value) : null })
                }
              />
            )}
          </Field>
        ) : null}

        <fieldset className="grid gap-3">
          <legend className="font-bold text-parchment">Actions it may use</legend>
          {TOOL_GROUPS.map((group) => (
            <Choice
              key={group.id}
              type="checkbox"
              title={group.name}
              meaning={group.meaning}
              checked={draft.tool_groups.includes(group.id)}
              onChange={() => update({ tool_groups: toggle(draft.tool_groups, group.id) })}
            />
          ))}
          <FieldError error={errors.tool_groups} />
        </fieldset>

        <ListField
          label="Knows"
          hint="What this persona knows before it starts, for example general web conventions."
          items={draft.knowledge.knows}
          placeholder="screen reader navigation"
          onChange={(knows) => update({ knowledge: { ...draft.knowledge, knows } })}
        />
        <ListField
          label="Does not know"
          hint="Terms it does not know until it has seen them on the site (limit L4)."
          items={draft.knowledge.does_not_know}
          placeholder="loyalty points"
          onChange={(does_not_know) => update({ knowledge: { ...draft.knowledge, does_not_know } })}
        />

        {problem ? (
          <p role="alert" className="font-bold text-rose">
            {problem}
            {errors.form ? ` ${errors.form}` : ""}
          </p>
        ) : null}
        <div className="flex flex-wrap gap-3">
          <button type="submit" className="pixel-button" disabled={saving}>
            {saving ? "Saving…" : personaId ? "Save changes" : "Save persona"}
          </button>
          <Link href="/studio/personas" className="pixel-button quiet">
            Cancel
          </Link>
          {personaId ? (
            <button type="button" className="pixel-button quiet ml-auto" onClick={remove}>
              Delete persona
            </button>
          ) : null}
        </div>
      </form>

      <aside className="pixel-panel lit flex h-fit flex-col gap-4 lg:sticky lg:top-6" aria-label="Preview">
        <p className="font-display text-sm uppercase tracking-widest text-amber">Preview</p>
        <div className="flex justify-center">
          <Sprite id={draft.character} scale={6} />
        </div>
        <div>
          <p className="font-display text-3xl font-bold text-parchment">
            {draft.name || character.name}
          </p>
          <p className="text-mist">{draft.represents || "Who does this persona represent?"}</p>
        </div>
        <div>
          <p className="font-bold text-parchment">Limits</p>
          {draft.limits.length ? (
            <ul className="list-disc pl-5 text-mist">
              {LIMITS.filter((limit) => draft.limits.includes(limit.id)).map((limit) => (
                <li key={limit.id}>{limit.meaning}</li>
              ))}
            </ul>
          ) : (
            <p className="text-mist">None: it behaves like an unrestricted agent.</p>
          )}
        </div>
        <p className="text-parchment">
          Will be saved as{" "}
          {status === "full" ? (
            <strong className="text-moss">a full persona</strong>
          ) : (
            <>
              <span className="preview-badge">Preview</span>
              <span className="block text-sm text-mist">
                Its limits are stated to the model but not enforced, so its trials run
                prompt-only. A persona is full only when it matches a validated built-in persona
                (Knock or Cog) in limits, perception and actions.
              </span>
            </>
          )}
        </p>
        {advice.length ? (
          <div>
            <p className="font-bold text-amber">Check these</p>
            <ul className="list-disc pl-5 text-mist">
              {advice.map((text) => (
                <li key={text}>{text}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </aside>
    </div>
  );
}
