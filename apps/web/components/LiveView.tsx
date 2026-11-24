"use client";

import { useEffect, useState } from "react";
import { api, type Step } from "@/lib/api";
import type { CharacterId } from "@/lib/cast";
import { Sprite } from "./Sprite";

const FRAME_MS = 250; // about four pictures a second while the run goes
const RETRY_MS = 1000; // no picture yet (the browser is starting): try again soon

/**
 * The test browser while the run goes: the latest screencast frame from the API,
 * refreshed several times a second, with the character overlay (the HUD) inside
 * the page. Until the first frame arrives, the latest step screenshot is shown.
 */
export function LiveView({
  runId,
  characterId,
  latest,
}: {
  runId: string;
  characterId: CharacterId | null;
  latest: Step | undefined;
}) {
  const [tick, setTick] = useState(0);
  const [wait, setWait] = useState<number | null>(null);
  const [seen, setSeen] = useState(false);
  const step = latest ? latest.index + 1 : 0;

  useEffect(() => {
    if (wait == null) return;
    const timer = window.setTimeout(() => {
      setWait(null);
      setTick((t) => t + 1);
    }, wait);
    return () => window.clearTimeout(timer);
  }, [wait]);

  return (
    <figure className="pixel-panel grid gap-3">
      <div className="flex flex-wrap items-center gap-3">
        <span className="live-badge" aria-hidden="true">
          Live
        </span>
        {characterId ? <Sprite id={characterId} scale={2} mood="walk" /> : null}
        <p className="text-sm text-mist" aria-live="polite">
          {step > 0
            ? `Step ${step}${latest?.proposed ? `: ${latest.proposed.tool}` : ""}`
            : "Starting the browser…"}
        </p>
      </div>
      {/* eslint-disable-next-line @next/next/no-img-element -- frames served by the API */}
      <img
        src={`${api.liveFrameUrl(runId)}?t=${tick}`}
        alt="The test browser, live, with the character's overlay"
        className={seen ? "w-full rounded border border-line" : "hidden"}
        onLoad={() => {
          setSeen(true);
          setWait(FRAME_MS);
        }}
        onError={() => setWait(RETRY_MS)}
      />
      {!seen && latest?.observation.screenshot_path ? (
        /* eslint-disable-next-line @next/next/no-img-element -- served by the API */
        <img
          src={api.screenshotUrl(runId, latest.index)}
          alt={`The browser before step ${latest.index + 1}`}
          className="w-full rounded border border-line"
        />
      ) : null}
      {!seen && !latest?.observation.screenshot_path ? (
        <p className="text-mist">Waiting for the first picture…</p>
      ) : null}
      <figcaption className="text-sm text-mist">
        {latest ? latest.observation.url : "Opening the start page"}
      </figcaption>
    </figure>
  );
}
