/**
 * The configuration studio's client: custom personas, sites and tasks (/studio/* in the
 * API, backend/vanguard/routes/studio.py). Types mirror backend/vanguard/contracts.
 * Built-in items are read-only; the server sets ids and a persona's status.
 */

import { API_BASE } from "./api";
import type { CharacterId } from "./cast";

export type LimitId = "L1" | "L2" | "L3" | "L4";
export type Perception = "full" | "accessibility_tree" | "magnified";
export type ToolGroup =
  | "keyboard"
  | "pointer"
  | "screen_reader"
  | "magnifier"
  | "navigation"
  | "control";
export type Scenario =
  | "search"
  | "add_to_cart"
  | "checkout"
  | "form"
  | "recovery"
  | "information";

export type PersonaSpec = {
  id: string;
  name: string;
  character: CharacterId;
  represents: string;
  status: "full" | "preview";
  limits: LimitId[];
  perception: Perception;
  tool_groups: ToolGroup[];
  knowledge: { knows: string[]; does_not_know: string[] };
  magnification: number | null;
  description: string;
  is_control: boolean;
};

export type PersonaDraft = Omit<PersonaSpec, "id" | "status" | "is_control">;

export type StudioSite = {
  id: string;
  name: string;
  origin: string;
  kind: string;
  description: string;
};

export type SiteDraft = Pick<StudioSite, "name" | "origin" | "description">;

export type SuccessCheck = {
  url_prefix: string | null;
  text_present: string | null;
  answer_contains: string[];
};

export type StudioTask = {
  id: string;
  site_id: string;
  instruction: string;
  scenario: Scenario | null;
  start_path: string;
  success: SuccessCheck;
  expected: Record<string, string>;
};

export type TaskDraft = Omit<StudioTask, "id" | "expected">;

/** Custom items have ids made by the server, always starting with this. */
export const isCustom = (id: string) => id.startsWith("custom-");

/** The plain-language meaning of each limit, from docs/leakage-spec.md, Section 3. */
export const LIMITS: { id: LimitId; name: string; meaning: string }[] = [
  {
    id: "L1",
    name: "No pointer",
    meaning:
      "Cannot use a mouse, trackpad or touch screen. Moves and acts with the keyboard only.",
  },
  {
    id: "L2",
    name: "Accessibility tree only",
    meaning:
      "Cannot see the screen. Knows only what assistive technology announces: roles, names and states, never colour, position or pictures.",
  },
  {
    id: "L3",
    name: "Magnified view",
    meaning:
      "Sees only a small magnified part of the page at a time, and must move the view to see more.",
  },
  {
    id: "L4",
    name: "First-time visitor",
    meaning:
      "Knows nothing about this site (its pages, product names, prices or codes) until it has seen them.",
  },
];

export const PERCEPTIONS: { id: Perception; name: string; meaning: string }[] = [
  { id: "full", name: "Full view", meaning: "The whole page, as a sighted user sees it." },
  {
    id: "accessibility_tree",
    name: "Accessibility tree",
    meaning: "Only the roles, names and states a screen reader announces.",
  },
  {
    id: "magnified",
    name: "Magnified window",
    meaning: "Only what fits in the zoomed-in window on the page.",
  },
];

export const TOOL_GROUPS: { id: ToolGroup; name: string; meaning: string }[] = [
  { id: "keyboard", name: "Keyboard", meaning: "Press keys (Tab, arrows, Enter, Space) and type text." },
  { id: "pointer", name: "Pointer", meaning: "Click, hover, drag and scroll with a mouse." },
  {
    id: "screen_reader",
    name: "Screen reader",
    meaning: "Jump to the next heading, link, field or landmark, read and activate it.",
  },
  { id: "magnifier", name: "Magnifier", meaning: "Move the magnified view, or bring the focused element into it." },
  { id: "navigation", name: "Navigation", meaning: "Open a link's address, go back and reload." },
  { id: "control", name: "Control", meaning: "Finish the task with an answer, or give up. Needed to end a run." },
];

export const CHARACTERS: CharacterId[] = ["knock", "echo", "iris", "wren", "cog"];

export const SCENARIOS: { id: Scenario; name: string }[] = [
  { id: "search", name: "Search: find something" },
  { id: "add_to_cart", name: "Add to cart or basket" },
  { id: "checkout", name: "Checkout or booking" },
  { id: "form", name: "Fill in a form" },
  { id: "recovery", name: "Recover from an error" },
  { id: "information", name: "Find a piece of information" },
];

/** A failed request. `fields` holds the server's message for each field it rejected. */
export class StudioError extends Error {
  constructor(
    message: string,
    public status: number,
    public fields: Record<string, string> = {},
  ) {
    super(message);
  }
}

type Detail = string | { loc?: (string | number)[]; msg?: string }[] | undefined;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
      cache: "no-store",
    });
  } catch {
    throw new StudioError("The Vanguard API is not reachable. Is the backend running?", 0);
  }
  if (response.status === 204) return undefined as T;
  if (!response.ok) {
    let detail: Detail;
    try {
      detail = ((await response.json()) as { detail?: Detail }).detail;
    } catch {
      // The body was not JSON: keep the status code.
    }
    if (Array.isArray(detail)) {
      const fields: Record<string, string> = {};
      for (const item of detail) {
        const field = String(item.loc?.[1] ?? "form");
        fields[field] = fields[field] ? `${fields[field]} ${item.msg}` : (item.msg ?? "");
      }
      throw new StudioError("Some answers need fixing.", response.status, fields);
    }
    throw new StudioError(detail ?? `The request failed (${response.status}).`, response.status);
  }
  return (await response.json()) as T;
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  body: JSON.stringify(body),
});
const at = (kind: string, id: string) => `/studio/${kind}/${encodeURIComponent(id)}`;

export const studio = {
  /** Built-in and custom personas together, as the lobby sees them. */
  allPersonas: () => request<PersonaSpec[]>("/personas"),
  persona: (id: string) => request<PersonaSpec>(at("personas", id)),
  createPersona: (draft: PersonaDraft) => request<PersonaSpec>("/studio/personas", json("POST", draft)),
  updatePersona: (id: string, draft: PersonaDraft) =>
    request<PersonaSpec>(at("personas", id), json("PUT", draft)),
  deletePersona: (id: string) => request<void>(at("personas", id), { method: "DELETE" }),

  /** Built-in and custom sites together. */
  allSites: () => request<StudioSite[]>("/sites"),
  site: (id: string) => request<StudioSite>(at("sites", id)),
  createSite: (draft: SiteDraft) => request<StudioSite>("/studio/sites", json("POST", draft)),
  updateSite: (id: string, draft: SiteDraft) => request<StudioSite>(at("sites", id), json("PUT", draft)),
  deleteSite: (id: string) => request<void>(at("sites", id), { method: "DELETE" }),

  /** Built-in and custom tasks on one site. */
  siteTasks: (siteId: string) =>
    request<StudioTask[]>(`/sites/${encodeURIComponent(siteId)}/tasks`),
  createTask: (draft: TaskDraft) => request<StudioTask>("/studio/tasks", json("POST", draft)),
  updateTask: (id: string, draft: TaskDraft) => request<StudioTask>(at("tasks", id), json("PUT", draft)),
  deleteTask: (id: string) => request<void>(at("tasks", id), { method: "DELETE" }),
};

/**
 * The status the server will give a persona: full only when its limits, perception,
 * tool groups and magnification match a built-in full persona exactly
 * (backend/vanguard/studio/repository.py, persona_status). Shown as a preview only;
 * the server decides.
 */
export function expectedStatus(draft: PersonaDraft, builtins: PersonaSpec[]): "full" | "preview" {
  const same = (a: string[], b: string[]) =>
    a.length === b.length && [...a].sort().join() === [...b].sort().join();
  const magnification = draft.perception === "magnified" ? draft.magnification : null;
  return builtins.some(
    (persona) =>
      !isCustom(persona.id) &&
      persona.status === "full" &&
      same(persona.limits, draft.limits) &&
      persona.perception === draft.perception &&
      same(persona.tool_groups, draft.tool_groups) &&
      (persona.magnification ?? null) === (magnification ?? null),
  )
    ? "full"
    : "preview";
}
