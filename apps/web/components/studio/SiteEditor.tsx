"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useState } from "react";
import { type SiteDraft, type StudioSite, studio, StudioError } from "@/lib/studio";
import { Field, INPUT } from "./fields";

/** The origin of a site address, or a message saying what is wrong with it. */
export function checkOrigin(value: string): { origin?: string; error?: string } {
  let url: URL;
  try {
    url = new URL(value.trim());
  } catch {
    return { error: "Enter the full address, starting with http:// or https://, for example https://shop.example.com." };
  }
  if (url.protocol !== "http:" && url.protocol !== "https:")
    return { error: "The address must start with http:// or https://." };
  if (!url.hostname) return { error: "The address must name a host, for example shop.example.com." };
  if (url.pathname !== "/" || url.search || url.hash)
    return {
      error:
        "Give only the site's address, without a page path, for example https://shop.example.com. Each task gives its own start page.",
    };
  return { origin: url.origin };
}

/** Add a site (no site given) or edit a custom one. */
export function SiteEditor({ site, onSaved }: { site?: StudioSite; onSaved?: (site: StudioSite) => void }) {
  const router = useRouter();
  const [draft, setDraft] = useState<SiteDraft>({
    name: site?.name ?? "",
    origin: site?.origin ?? "",
    description: site?.description ?? "",
  });
  const [allowed, setAllowed] = useState(Boolean(site));
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [problem, setProblem] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  async function save(event: FormEvent) {
    event.preventDefault();
    setNotice("");
    setProblem("");
    const found: Record<string, string> = {};
    if (!draft.name.trim()) found.name = "Give the site a name.";
    const checked = checkOrigin(draft.origin);
    if (checked.error) found.origin = checked.error;
    if (!allowed) found.allowed = "Confirm that you own this site or are allowed to test it.";
    setErrors(found);
    if (Object.keys(found).length) {
      setProblem("Some answers need fixing.");
      return;
    }
    setSaving(true);
    const body = { ...draft, origin: checked.origin ?? draft.origin };
    try {
      const saved = site ? await studio.updateSite(site.id, body) : await studio.createSite(body);
      if (site) {
        setDraft({ name: saved.name, origin: saved.origin, description: saved.description });
        setNotice("Saved.");
        onSaved?.(saved);
      } else {
        router.push(`/studio/sites/${encodeURIComponent(saved.id)}`);
      }
    } catch (error) {
      if (error instanceof StudioError) {
        setErrors(error.fields);
        setProblem(error.message);
      } else setProblem("The site could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  async function remove() {
    if (!site) return;
    try {
      await studio.deleteSite(site.id);
      router.push("/studio/sites");
    } catch (error) {
      setProblem(error instanceof Error ? error.message : "The site could not be deleted.");
    }
  }

  return (
    <form className="pixel-panel grid gap-5" onSubmit={save} noValidate>
      <Field label="Name" hint="How the site is shown in the site picker." error={errors.name}>
        {(props) => (
          <input
            {...props}
            className={INPUT}
            value={draft.name}
            placeholder="Our online shop"
            onChange={(event) => setDraft({ ...draft, name: event.target.value })}
          />
        )}
      </Field>
      <Field
        label="Address"
        hint="The site's address (its origin), for example https://shop.example.com or http://localhost:3104. Simulated users may visit pages under this address only."
        error={errors.origin}
      >
        {(props) => (
          <input
            {...props}
            type="url"
            inputMode="url"
            className={INPUT}
            value={draft.origin}
            placeholder="https://shop.example.com"
            onChange={(event) => setDraft({ ...draft, origin: event.target.value })}
            onBlur={() => {
              const checked = checkOrigin(draft.origin);
              setErrors((current) => {
                const next = { ...current };
                delete next.origin;
                if (draft.origin && checked.error) next.origin = checked.error;
                return next;
              });
            }}
          />
        )}
      </Field>
      <Field label="Description (optional)" hint="What the site is, in a sentence or two." error={errors.description}>
        {(props) => (
          <textarea
            {...props}
            rows={3}
            className={INPUT}
            value={draft.description}
            onChange={(event) => setDraft({ ...draft, description: event.target.value })}
          />
        )}
      </Field>

      <div className="rounded border-2 border-amber bg-night p-4 text-parchment">
        <p className="font-bold text-amber">Only add sites you may test</p>
        <p className="mt-1 text-sm">
          Simulated users really visit the site, click, type and submit forms. Add only sites you
          own or have written permission to test, and never a live site where a form would send a
          real order, payment or message.
        </p>
        <label className="mt-3 flex cursor-pointer items-start gap-3">
          <input
            type="checkbox"
            className="round-check mt-0.5"
            checked={allowed}
            aria-invalid={Boolean(errors.allowed)}
            onChange={(event) => setAllowed(event.target.checked)}
          />
          <span>I own this site or am allowed to test it.</span>
        </label>
        {errors.allowed ? <p className="mt-1 text-sm font-bold text-rose">{errors.allowed}</p> : null}
      </div>

      {problem ? (
        <p role="alert" className="font-bold text-rose">
          {problem}
          {errors.form ? ` ${errors.form}` : ""}
        </p>
      ) : null}
      <p role="status" className="text-moss">
        {notice}
      </p>
      <div className="flex flex-wrap gap-3">
        <button type="submit" className="pixel-button" disabled={saving}>
          {saving ? "Saving…" : site ? "Save changes" : "Add the site"}
        </button>
        <Link href="/studio/sites" className="pixel-button quiet">
          {site ? "Back to sites" : "Cancel"}
        </Link>
        {site ? (
          confirmDelete ? (
            <span className="ml-auto flex flex-wrap items-center gap-2">
              <span className="text-parchment">Delete the site and its tasks?</span>
              <button type="button" className="pixel-button quiet" onClick={remove}>
                Yes, delete
              </button>
              <button type="button" className="pixel-button quiet" onClick={() => setConfirmDelete(false)}>
                Keep
              </button>
            </span>
          ) : (
            <button type="button" className="pixel-button quiet ml-auto" onClick={() => setConfirmDelete(true)}>
              Delete site
            </button>
          )
        ) : null}
      </div>
    </form>
  );
}
