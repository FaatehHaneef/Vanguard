"use client";

import { useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import { api, type LabelItem, type LabelVerdict } from "@/lib/api";

const LIMITS: [string, string][] = [
  ["L1", "L1 No pointer"],
  ["L2", "L2 Accessibility tree only"],
  ["L3", "L3 Magnified view"],
  ["L4", "L4 First-time visitor"],
];
const NAME_KEY = "vanguard.labeller";

function savedName(): string {
  try {
    return window.localStorage.getItem(NAME_KEY) ?? "";
  } catch {
    return ""; // Storage may be blocked; the labeller types their name again.
  }
}
const noSubscription = () => () => undefined;

function describe(item: LabelItem): string {
  const action = item.step.proposed;
  if (!action) return "(no valid action)";
  const args = Object.entries(action)
    .filter(
      ([key, value]) => key !== "tool" && key !== "rationale" && value != null,
    )
    .map(([key, value]) => `${key}=${JSON.stringify(value)}`);
  return `${action.tool}(${args.join(", ")})`;
}

/**
 * Blind labelling: one step at a time, never showing the checker's verdict.
 * See docs/labelling-guide.md.
 */
export function LabelDesk() {
  const stored = useSyncExternalStore(noSubscription, savedName, () => "");
  // A labelling bundle is imported as a batch; ?batch= limits the desk to its fixed sample.
  const batch = useSearchParams().get("batch") ?? undefined;
  const [chosen, setChosen] = useState<string | null>(null);
  const name = chosen ?? stored;
  const [draftName, setDraftName] = useState("");
  const [queue, setQueue] = useState<LabelItem[]>([]);
  const [labelled, setLabelled] = useState(0);
  const [verdict, setVerdict] = useState<LabelVerdict | null>(null);
  const [limit, setLimit] = useState("L1");
  const [kind, setKind] = useState<"action" | "information">("action");
  const [note, setNote] = useState("");
  const [message, setMessage] = useState("");

  const refill = useCallback(
    (who: string) =>
      Promise.all([api.nextToLabel(who, 10, batch), api.labels(who)]).then(
        ([items, done]) => {
          setQueue(items);
          setLabelled(done.length);
          setMessage(items.length ? "" : "Nothing left to label. Thank you.");
        },
        () =>
          setMessage(
            "The labelling queue could not be loaded. Is the API running?",
          ),
      ),
    [batch],
  );

  useEffect(() => {
    if (!name) return;
    let live = true;
    Promise.all([api.nextToLabel(name, 10, batch), api.labels(name)]).then(
      ([items, done]) => {
        if (!live) return;
        setQueue(items);
        setLabelled(done.length);
        setMessage(items.length ? "" : "Nothing left to label. Thank you.");
      },
      () =>
        live &&
        setMessage(
          "The labelling queue could not be loaded. Is the API running?",
        ),
    );
    return () => {
      live = false;
    };
  }, [name, batch]);

  const item = queue[0];

  async function submit() {
    if (!item || !verdict) return;
    if (verdict === "unsure" && !note.trim()) {
      setMessage("Please say briefly why you are unsure.");
      return;
    }
    try {
      await api.saveLabel({
        run_id: item.run_id,
        index: item.index,
        labeller: name,
        verdict,
        limit: verdict === "yes" ? limit : null,
        kind: verdict === "yes" ? kind : null,
        note: note.trim(),
      });
      setVerdict(null);
      setNote("");
      setMessage("");
      setLabelled((count) => count + 1);
      const rest = queue.slice(1);
      setQueue(rest);
      if (rest.length === 0) void refill(name);
    } catch (error) {
      setMessage(`Not saved: ${(error as Error).message}`);
    }
  }

  if (!name) {
    return (
      <form
        className="pixel-panel grid max-w-md gap-3"
        onSubmit={(event) => {
          event.preventDefault();
          const who = draftName.trim();
          if (!who) return;
          try {
            window.localStorage.setItem(NAME_KEY, who);
          } catch {
            // Fine: the name lasts for this visit only.
          }
          setChosen(who);
        }}
      >
        <label
          htmlFor="labeller"
          className="font-display text-lg text-parchment"
        >
          Your labeller name
        </label>
        <input
          id="labeller"
          value={draftName}
          onChange={(event) => setDraftName(event.target.value)}
          className="rounded border border-line bg-night px-3 py-2 text-parchment"
          autoComplete="nickname"
          maxLength={40}
        />
        <button type="submit" className="pixel-button">
          Start labelling
        </button>
      </form>
    );
  }

  return (
    <div className="grid gap-4">
      <p className="text-mist">
        Labelling as <strong className="text-parchment">{name}</strong> ·{" "}
        {labelled} labelled ·{" "}
        <button
          type="button"
          className="underline"
          onClick={() => {
            setChosen("");
            setQueue([]);
          }}
        >
          switch labeller
        </button>
      </p>
      {message ? (
        <p role="status" className="font-bold text-amber">
          {message}
        </p>
      ) : null}
      {item ? (
        <article
          className="pixel-panel grid gap-3"
          aria-labelledby="item-title"
        >
          <h2 id="item-title" className="font-display text-xl text-amber">
            Item {item.position + 1}: {item.persona_name}, step {item.index + 1}
          </h2>
          <p className="text-sm text-mist">
            Limits:{" "}
            {item.persona_limits.join(", ") ||
              "none (control: judge every limit)"}
          </p>
          <p className="text-parchment">{item.persona_description}</p>
          <p className="text-parchment">
            <span className="text-mist">Task:</span> {item.task}
          </p>
          {item.step.observation.screenshot_path ? (
            // eslint-disable-next-line @next/next/no-img-element -- served by the API
            <img
              src={api.screenshotUrl(item.run_id, item.index)}
              alt="What the browser showed before this step"
              className="w-full max-w-3xl rounded border border-line"
            />
          ) : null}
          <details>
            <summary className="cursor-pointer text-mist">
              What the persona perceived ({item.step.observation.url})
            </summary>
            <pre className="mt-2 max-h-72 overflow-auto whitespace-pre-wrap rounded bg-night p-2 text-sm text-parchment">
              {item.step.observation.content}
            </pre>
          </details>
          <p>
            <span className="text-mist">Proposed:</span>{" "}
            <code className="text-parchment">{describe(item)}</code>
          </p>
          {item.step.proposed?.rationale ? (
            <p className="text-sm italic text-mist">
              &ldquo;{item.step.proposed.rationale}&rdquo;
            </p>
          ) : null}
          <p className="text-sm text-mist">
            Gate:{" "}
            {item.step.gate.allowed
              ? "allowed"
              : `refused (${item.step.gate.rule})`}{" "}
            · Executed: {item.step.executed ? "yes" : "no"} · Browser events:{" "}
            {item.step.events
              .map((e) => `${e.type}${e.trusted ? "" : " (untrusted)"}`)
              .join(", ") || "none"}
          </p>

          <fieldset className="grid gap-2">
            <legend className="font-display text-parchment">
              Did this step break a limit of this persona?
            </legend>
            <div className="flex flex-wrap gap-2">
              {(["no", "yes", "unsure"] as LabelVerdict[]).map((option) => (
                <button
                  key={option}
                  type="button"
                  aria-pressed={verdict === option}
                  className={`pixel-button ${verdict === option ? "" : "quiet"}`}
                  onClick={() => setVerdict(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </fieldset>
          {verdict === "yes" ? (
            <div className="flex flex-wrap gap-4">
              <label className="grid gap-1 text-sm text-mist">
                Which limit
                <select
                  value={limit}
                  onChange={(event) => setLimit(event.target.value)}
                  className="rounded border border-line bg-night px-2 py-1 text-parchment"
                >
                  {LIMITS.map(([value, text]) => (
                    <option key={value} value={value}>
                      {text}
                    </option>
                  ))}
                </select>
              </label>
              <label className="grid gap-1 text-sm text-mist">
                Kind
                <select
                  value={kind}
                  onChange={(event) =>
                    setKind(event.target.value as "action" | "information")
                  }
                  className="rounded border border-line bg-night px-2 py-1 text-parchment"
                >
                  <option value="action">action</option>
                  <option value="information">information</option>
                </select>
              </label>
            </div>
          ) : null}
          <label className="grid gap-1 text-sm text-mist">
            Note {verdict === "unsure" ? "(required)" : "(optional)"}
            <textarea
              value={note}
              onChange={(event) => setNote(event.target.value)}
              rows={2}
              maxLength={1000}
              className="rounded border border-line bg-night px-2 py-1 text-parchment"
            />
          </label>
          <button
            type="button"
            className="pixel-button"
            disabled={!verdict}
            onClick={submit}
          >
            Save and next
          </button>
        </article>
      ) : null}
    </div>
  );
}
