"use client";

import { type ReactNode, useId, useState } from "react";

export const INPUT =
  "w-full rounded border-2 border-slate bg-night px-3 py-2 text-parchment placeholder:text-mist/70 focus:border-amber aria-[invalid=true]:border-rose";

/** A labelled field with an optional hint and the server's error under it. */
export function Field({
  label,
  hint,
  error,
  children,
}: {
  label: string;
  hint?: string;
  error?: string;
  children: (props: { id: string; "aria-describedby"?: string; "aria-invalid": boolean }) => ReactNode;
}) {
  const id = useId();
  const described = [hint ? `${id}-hint` : "", error ? `${id}-error` : ""].filter(Boolean).join(" ");
  return (
    <div className="grid gap-1">
      <label htmlFor={id} className="font-bold text-parchment">
        {label}
      </label>
      {hint ? (
        <p id={`${id}-hint`} className="text-sm text-mist">
          {hint}
        </p>
      ) : null}
      {children({ id, "aria-describedby": described || undefined, "aria-invalid": Boolean(error) })}
      <FieldError id={`${id}-error`} error={error} />
    </div>
  );
}

export function FieldError({ id, error }: { id?: string; error?: string }) {
  return error ? (
    <p id={id} className="text-sm font-bold text-rose">
      {error}
    </p>
  ) : null;
}

/** A list of short texts with an add box and a remove button for each entry. */
export function ListField({
  label,
  hint,
  items,
  onChange,
  placeholder,
}: {
  label: string;
  hint?: string;
  items: string[];
  onChange: (items: string[]) => void;
  placeholder?: string;
}) {
  const id = useId();
  const [draft, setDraft] = useState("");
  const add = () => {
    const text = draft.trim();
    if (text && !items.includes(text)) onChange([...items, text]);
    setDraft("");
  };
  return (
    <fieldset className="grid gap-2">
      <legend className="font-bold text-parchment">{label}</legend>
      {hint ? <p className="text-sm text-mist">{hint}</p> : null}
      {items.length ? (
        <ul className="flex flex-wrap gap-2">
          {items.map((item) => (
            <li key={item} className="flex items-center gap-1 rounded bg-slate px-2 py-1 text-parchment">
              {item}
              <button
                type="button"
                className="rounded px-1 text-amber hover:bg-night"
                aria-label={`Remove ${item}`}
                onClick={() => onChange(items.filter((entry) => entry !== item))}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <div className="flex gap-2">
        <label htmlFor={id} className="sr-only">
          Add to {label.toLowerCase()}
        </label>
        <input
          id={id}
          className={INPUT}
          value={draft}
          placeholder={placeholder}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              add();
            }
          }}
        />
        <button type="button" className="pixel-button quiet" onClick={add}>
          Add
        </button>
      </div>
    </fieldset>
  );
}

/** A checkbox or radio button named by `title`, with `meaning` as its description. */
export function Choice({
  type,
  name,
  checked,
  onChange,
  title,
  meaning,
}: {
  type: "checkbox" | "radio";
  name?: string;
  checked: boolean;
  onChange: () => void;
  title: string;
  meaning: string;
}) {
  const id = useId();
  return (
    <div className="flex items-start gap-3">
      <input
        id={id}
        type={type}
        name={name}
        className={type === "checkbox" ? "round-check mt-1" : "mt-1 size-5 accent-amber"}
        checked={checked}
        onChange={onChange}
        aria-describedby={`${id}-meaning`}
      />
      <div>
        <label htmlFor={id} className="cursor-pointer font-bold text-parchment">
          {title}
        </label>
        <p id={`${id}-meaning`} className="text-mist">
          {meaning}
        </p>
      </div>
    </div>
  );
}
