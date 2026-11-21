/**
 * The Vanguard HUD: a persona's character walking to the element it acts on.
 *
 * Decoration only. Playwright adds this script to the browser session from outside;
 * the website never ships it. It lives in a closed shadow root on a host marked
 * `data-vanguard-hud`, `aria-hidden` and `inert`, with `pointer-events: none`, so it
 * receives no input, takes no focus, is absent from the accessibility tree and is
 * skipped by the observation builder (backend/vanguard/executor/js/observe.js).
 *
 * The animation table and the walking approach are adapted from Sentinel's
 * engine/hud/stage.ts (same author, MIT; see NOTICE.md). The art is the web app's
 * (apps/web/lib/art), imported rather than copied.
 */

import { COG_FRAMES, COG_PALETTE } from "../../web/lib/art/cog";
import { ECHO_FRAMES, ECHO_PALETTE } from "../../web/lib/art/echo";
import { IRIS_FRAMES, IRIS_PALETTE } from "../../web/lib/art/iris";
import { KNOCK_FRAMES, KNOCK_PALETTE } from "../../web/lib/art/knock";
import { WREN_FRAMES, WREN_PALETTE } from "../../web/lib/art/wren";

type Frames = Record<string, readonly string[]>;
type Palette = Record<string, string>;

const ART: Record<string, { frames: Frames; palette: Palette }> = {
  knock: { frames: KNOCK_FRAMES, palette: KNOCK_PALETTE },
  echo: { frames: ECHO_FRAMES, palette: ECHO_PALETTE },
  iris: { frames: IRIS_FRAMES, palette: IRIS_PALETTE },
  wren: { frames: WREN_FRAMES, palette: WREN_PALETTE },
  cog: { frames: COG_FRAMES, palette: COG_PALETTE },
};

export type Mood = "walk" | "idle" | "worry" | "happy";
export type Tone = "act" | "refused" | "done" | "info";
export type Box = { x: number; y: number; width: number; height: number };

const SEQUENCES: Record<Mood, { frames: string[]; perSecond: number }> = {
  idle: { frames: ["idle"], perSecond: 1 },
  walk: { frames: ["walk1", "idle", "walk2", "idle"], perSecond: 8 },
  worry: { frames: ["worry"], perSecond: 1 },
  happy: { frames: ["happy"], perSecond: 1 },
};

const SCALE = 3;
const WALK_SPEED = 900; // CSS pixels per second
const MAX_WALK_MS = 400;
const KEY = Symbol.for("vanguard.hud");

const STYLES = `
  :host { all: initial; }
  .layer { position: fixed; inset: 0; pointer-events: none; z-index: 2147483647;
    font: 600 13px/1.3 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  canvas.sprite { position: absolute; left: 0; top: 0; image-rendering: pixelated;
    filter: drop-shadow(0 2px 0 rgba(18, 21, 42, 0.45));
    transition-property: transform; transition-timing-function: linear; }
  .ring { position: absolute; border: 3px dashed #ffb347; border-radius: 4px;
    box-shadow: 0 0 0 2px rgba(18, 21, 42, 0.6); transition: all 180ms ease-out; opacity: 0; }
  .ring.on { opacity: 1; }
  .ring.refused { border-color: #e05a6d; }
  .bubble { position: absolute; max-width: 320px; padding: 6px 9px; border-radius: 4px;
    background: #1b1f3b; color: #f3e9d2; border: 2px solid #ffb347; white-space: pre-wrap;
    opacity: 0; transition: opacity 150ms; }
  .bubble.on { opacity: 1; }
  .bubble.refused { border-color: #e05a6d; }
  .bubble.done { border-color: #7fb069; }
  .tag { position: fixed; left: 12px; bottom: 12px; padding: 4px 8px; border-radius: 3px;
    background: rgba(27, 31, 59, 0.85); color: #f3e9d2; font-size: 11px; letter-spacing: 0.08em;
    text-transform: uppercase; }
`;

function buildFrames(frames: Frames, palette: Palette): Record<string, HTMLCanvasElement> {
  const built: Record<string, HTMLCanvasElement> = {};
  for (const [name, rows] of Object.entries(frames)) {
    const canvas = document.createElement("canvas");
    canvas.width = rows[0].length;
    canvas.height = rows.length;
    const context = canvas.getContext("2d");
    if (!context) continue;
    rows.forEach((row, y) => {
      for (let x = 0; x < row.length; x++) {
        const colour = palette[row[x]];
        if (!colour) continue;
        context.fillStyle = colour;
        context.fillRect(x, y, 1, 1);
      }
    });
    built[name] = canvas;
  }
  return built;
}

class Hud {
  private readonly host: HTMLElement;
  private readonly sprite: HTMLCanvasElement;
  private readonly context: CanvasRenderingContext2D;
  private readonly ring: HTMLDivElement;
  private readonly bubble: HTMLDivElement;
  private readonly tag: HTMLDivElement;
  private frames: Record<string, HTMLCanvasElement> = {};
  private character = "";
  private x = 24;
  private y = 0;
  private facing: 1 | -1 = 1;
  private mood: Mood = "idle";
  private settled: Mood = "idle";
  private frameIndex = 0;
  private arrival = 0;

  constructor() {
    this.host = document.createElement("div");
    this.host.setAttribute("data-vanguard-hud", "");
    this.host.setAttribute("aria-hidden", "true");
    this.host.setAttribute("inert", "");
    this.host.style.cssText = "position:fixed;inset:0;pointer-events:none;z-index:2147483647";
    const root = this.host.attachShadow({ mode: "closed" });
    const style = document.createElement("style");
    style.textContent = STYLES;
    const layer = document.createElement("div");
    layer.className = "layer";
    this.ring = document.createElement("div");
    this.ring.className = "ring";
    this.sprite = document.createElement("canvas");
    this.sprite.className = "sprite";
    this.bubble = document.createElement("div");
    this.bubble.className = "bubble";
    this.tag = document.createElement("div");
    this.tag.className = "tag";
    layer.append(this.ring, this.sprite, this.bubble, this.tag);
    root.append(style, layer);
    const context = this.sprite.getContext("2d");
    if (!context) throw new Error("canvas unavailable");
    this.context = context;
    this.y = window.innerHeight - 120;
    this.attach();
    this.place(0);
    // Timers rather than animation frames: they also run in a headless browser, so the
    // screenshots show the character where it should be.
    setInterval(this.animate, 1000 / SEQUENCES.walk.perSecond);
  }

  /** Pages may replace the body; put the host back whenever it goes missing. */
  attach(): void {
    if (!this.host.isConnected) document.documentElement.append(this.host);
  }

  setCharacter(id: string, label: string): void {
    this.attach();
    this.tag.textContent = label;
    if (id === this.character || !ART[id]) return;
    this.character = id;
    this.frames = buildFrames(ART[id].frames, ART[id].palette);
    const first = Object.values(this.frames)[0];
    this.sprite.width = first.width * SCALE;
    this.sprite.height = first.height * SCALE;
    this.context.imageSmoothingEnabled = false;
  }

  /** Walk to a box (viewport coordinates) and say what is happening there. */
  act(box: Box | null, text: string, tone: Tone): void {
    this.attach();
    const spriteW = this.sprite.width || 48;
    const spriteH = this.sprite.height || 72;
    this.settled = tone === "refused" ? "worry" : tone === "done" ? "happy" : "idle";
    if (!box) this.mood = this.settled;
    if (box) {
      const left = box.x - spriteW - 6;
      const x = left >= 4 ? left : Math.min(box.x + box.width + 6, window.innerWidth - spriteW - 4);
      const y = box.y + box.height - spriteH;
      this.moveTo(x, Math.max(4, Math.min(y, window.innerHeight - spriteH - 4)));
      Object.assign(this.ring.style, {
        left: `${box.x - 4}px`,
        top: `${box.y - 4}px`,
        width: `${box.width + 2}px`,
        height: `${box.height + 2}px`,
      });
      this.ring.className = `ring on ${tone === "refused" ? "refused" : ""}`;
    } else {
      this.ring.className = "ring";
    }
    this.bubble.textContent = text;
    this.bubble.className = `bubble on ${tone}`;
    this.placeBubble();
  }

  private moveTo(x: number, y: number): void {
    if (Math.abs(x - this.x) > 1) this.facing = x > this.x ? 1 : -1;
    const ms = Math.min(MAX_WALK_MS, (Math.hypot(x - this.x, y - this.y) / WALK_SPEED) * 1000);
    this.x = x;
    this.y = y;
    this.mood = ms > 20 ? "walk" : this.settled;
    this.place(ms);
    window.clearTimeout(this.arrival);
    this.arrival = window.setTimeout(() => {
      this.mood = this.settled;
      this.draw();
    }, ms);
  }

  private place(ms: number): void {
    this.sprite.style.transitionDuration = `${ms}ms`;
    this.sprite.style.transform = `translate(${this.x}px, ${this.y}px) scaleX(${this.facing})`;
  }

  private placeBubble(): void {
    const spriteW = this.sprite.width || 48;
    const width = this.bubble.offsetWidth || 160;
    const x = Math.max(4, Math.min(this.x + spriteW / 2 - width / 2, window.innerWidth - width - 4));
    const above = this.y - (this.bubble.offsetHeight || 28) - 8;
    this.bubble.style.left = `${x}px`;
    this.bubble.style.top = `${above >= 4 ? above : this.y + (this.sprite.height || 72) + 8}px`;
  }

  private readonly animate = (): void => {
    this.frameIndex += 1;
    this.draw();
  };

  private draw(): void {
    const sequence = SEQUENCES[this.mood];
    const name = sequence.frames[this.frameIndex % sequence.frames.length];
    const frame = this.frames[name] ?? this.frames.idle;
    if (!frame) return;
    this.context.clearRect(0, 0, this.sprite.width, this.sprite.height);
    this.context.drawImage(frame, 0, 0, this.sprite.width, this.sprite.height);
  }
}

type HudApi = {
  show(character: string, label: string, box: Box | null, text: string, tone: Tone): void;
  settle(): Promise<void>;
};

function install(): void {
  const scope = window as unknown as Record<symbol, HudApi | undefined>;
  if (scope[KEY]) return;
  let hud: Hud | null = null;
  scope[KEY] = {
    show(character, label, box, text, tone) {
      if (!document.documentElement) return;
      hud ??= new Hud();
      hud.setCharacter(character, label);
      hud.act(box, text, tone);
    },
    // Lets the executor wait until the walk has finished before a screenshot.
    settle: () => new Promise((resolve) => setTimeout(resolve, 450)),
  };
}

install();
