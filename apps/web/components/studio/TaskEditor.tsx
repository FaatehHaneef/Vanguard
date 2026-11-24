"use client";

import { type FormEvent, useState } from "react";
import {
  SCENARIOS,
  type Scenario,
  studio,
  StudioError,
  type StudioTask,
  type TaskDraft,
} from "@/lib/studio";
import { Choice, Field, FieldError, INPUT, ListField } from "./fields";

type CheckKind = "url_prefix" | "text_present" | "answer_contains";

const CHECKS: { id: CheckKind; name: string; meaning: string }[] = [
  {
    id: "url_prefix",
    name: "The page address starts with",
    meaning: "Done when the user reaches a page whose path starts with this, for example /order/confirmed.",
  },
  {
    id: "text_present",
    name: "Text appears on the page",
    meaning: "Done when this text is visible on the page, for example “Thank you for your order”.",
  },
  {
    id: "answer_contains",
    name: "The final answer contains",
    meaning: "For questions: done when the user’s answer contains every one of these words or numbers.",
  },
];

function kindOf(task?: StudioTask): CheckKind {
  if (!task) return "url_prefix";
  if (task.success.url_prefix) return "url_prefix";
  if (task.success.text_present) return "text_present";
  return "answer_contains";
}

/** Add a task to a site, or edit a custom task. */
export function TaskEditor({
  siteId,
  task,
  onSaved,
  onCancel,
}: {
  siteId: string;
  task?: StudioTask;
  onSaved: (task: StudioTask) => void;
  onCancel: () => void;
}) {
  const [instruction, setInstruction] = useState(task?.instruction ?? "");
  const [startPath, setStartPath] = useState(task?.start_path ?? "/");
  const [scenario, setScenario] = useState<Scenario | "">(task?.scenario ?? "");
  const [kind, setKind] = useState<CheckKind>(kindOf(task));
  const [value, setValue] = useState(task?.success.url_prefix ?? task?.success.text_present ?? "");
  const [words, setWords] = useState<string[]>(task?.success.answer_contains ?? []);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [problem, setProblem] = useState("");
  const [saving, setSaving] = useState(false);

  async function save(event: FormEvent) {
    event.preventDefault();
    const found: Record<string, string> = {};
    if (!instruction.trim()) found.instruction = "Say what the user is asked to do.";
    if (!startPath.trim().startsWith("/"))
      found.start_path = "The start page is a path on the site, starting with /, for example /menu.";
    if (!scenario) found.scenario = "Choose the kind of task.";
    if (kind === "answer_contains" ? !words.length : !value.trim())
      found.success =
        kind === "answer_contains"
          ? "Add at least one word or number the answer must contain."
          : "Fill in the success check.";
    else if (kind === "url_prefix" && !value.trim().startsWith("/"))
      found.success = "The address to reach is a path starting with /, for example /order/confirmed.";
    setErrors(found);
    setProblem(Object.keys(found).length ? "Some answers need fixing." : "");
    if (Object.keys(found).length) return;

    const draft: TaskDraft = {
      site_id: siteId,
      instruction: instruction.trim(),
      start_path: startPath.trim(),
      scenario: scenario || null,
      success: {
        url_prefix: kind === "url_prefix" ? value.trim() : null,
        text_present: kind === "text_present" ? value.trim() : null,
        answer_contains: kind === "answer_contains" ? words : [],
      },
    };
    setSaving(true);
    try {
      onSaved(task ? await studio.updateTask(task.id, draft) : await studio.createTask(draft));
    } catch (error) {
      if (error instanceof StudioError) {
        setErrors(error.fields);
        setProblem(error.message);
      } else setProblem("The task could not be saved.");
      setSaving(false);
    }
  }

  return (
    <form className="pixel-panel lit grid gap-5" onSubmit={save} noValidate aria-label={task ? "Edit task" : "New task"}>
      <Field
        label="Instruction"
        hint="What the simulated user is asked to do, in plain words, with any details it needs (names, quantities)."
        error={errors.instruction}
      >
        {(props) => (
          <textarea
            {...props}
            rows={3}
            className={INPUT}
            value={instruction}
            placeholder="Order one Masala Fries for pickup at 18:30, under the name Sara Khan."
            onChange={(event) => setInstruction(event.target.value)}
          />
        )}
      </Field>
      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Start page" hint="Where the user starts: a path on the site." error={errors.start_path}>
          {(props) => (
            <input
              {...props}
              className={`${INPUT} font-mono`}
              value={startPath}
              onChange={(event) => setStartPath(event.target.value)}
            />
          )}
        </Field>
        <Field label="Kind of task" hint="Used to group results by scenario." error={errors.scenario}>
          {(props) => (
            <select
              {...props}
              className={INPUT}
              value={scenario}
              onChange={(event) => setScenario(event.target.value as Scenario | "")}
            >
              <option value="">Choose…</option>
              {SCENARIOS.map((option) => (
                <option key={option.id} value={option.id}>
                  {option.name}
                </option>
              ))}
            </select>
          )}
        </Field>
      </div>

      <fieldset className="grid gap-3">
        <legend className="font-bold text-parchment">How Vanguard knows it was done</legend>
        <p className="text-sm text-mist">Checked by code after every step, never by a model.</p>
        {CHECKS.map((check) => (
          <Choice
            key={check.id}
            type="radio"
            name="check"
            title={check.name}
            meaning={check.meaning}
            checked={kind === check.id}
            onChange={() => setKind(check.id)}
          />
        ))}
        {kind === "answer_contains" ? (
          <ListField
            label="Words or numbers the answer must contain"
            items={words}
            placeholder="14.50"
            onChange={setWords}
          />
        ) : (
          <Field label={kind === "url_prefix" ? "Path to reach" : "Text to find"}>
            {(props) => (
              <input
                {...props}
                className={`${INPUT} ${kind === "url_prefix" ? "font-mono" : ""}`}
                value={value}
                placeholder={kind === "url_prefix" ? "/order/confirmed" : "Thank you for your order"}
                onChange={(event) => setValue(event.target.value)}
              />
            )}
          </Field>
        )}
        <FieldError error={errors.success} />
      </fieldset>

      {problem ? (
        <p role="alert" className="font-bold text-rose">
          {problem}
          {errors.site_id ? ` ${errors.site_id}` : ""}
          {errors.form ? ` ${errors.form}` : ""}
        </p>
      ) : null}
      <div className="flex flex-wrap gap-3">
        <button type="submit" className="pixel-button" disabled={saving}>
          {saving ? "Saving…" : task ? "Save the task" : "Add the task"}
        </button>
        <button type="button" className="pixel-button quiet" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}
