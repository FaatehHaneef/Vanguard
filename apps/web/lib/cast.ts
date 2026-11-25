/**
 * The cast: how each Vanguard persona looks and sounds in the UI.
 *
 * This file holds display data only. What a persona can perceive and do, and whether it
 * is a full or a preview persona, come from the API (GET /personas), so the UI can never
 * disagree with the backend. Characters are matched to personas by `character`.
 */

export type CharacterId =
  "knock" | "echo" | "iris" | "wren" | "cog" | "dash" | "pell" | "tobin";

export type Accent = "amber" | "ember" | "moss" | "mist" | "rose" | "parchment";

export type Character = {
  id: CharacterId;
  /** The persona this character plays, as in backend/vanguard/catalog/data/personas. */
  personaId: string;
  name: string;
  represents: string;
  motto: string;
  /** The limits this character lives with, in plain words. */
  limits: readonly string[];
  accent: Accent;
};

export const CAST: readonly Character[] = [
  {
    id: "knock",
    personaId: "keyboard-only",
    name: "Knock",
    represents: "A shopper who uses only a keyboard",
    motto: "Tab, tab, tab. Is anyone home?",
    limits: [
      "No mouse, trackpad or touch",
      "Moves with Tab, arrows, Enter and Space",
    ],
    accent: "parchment",
  },
  {
    id: "echo",
    personaId: "screen-reader",
    name: "Echo",
    represents: "A shopper who uses a screen reader",
    motto: "Tell me what it is, and I'll find my way.",
    limits: [
      "Cannot see the screen",
      "Knows only what the screen reader announces",
      "No mouse",
    ],
    accent: "rose",
  },
  {
    id: "iris",
    personaId: "magnifier",
    name: "Iris",
    represents: "A shopper with low vision who uses a magnifier",
    motto: "If I can't read it, dear, I can't buy it.",
    limits: [
      "Sees a quarter of the page at a time",
      "Must move the magnified view to see more",
    ],
    accent: "amber",
  },
  {
    id: "wren",
    personaId: "first-time",
    name: "Wren",
    represents: "A first-time visitor who knows nothing about the shop",
    motto: "Never been here. Where do I start?",
    limits: [
      "Knows nothing site-specific until seen",
      "No shop terms, codes or hidden pages",
    ],
    accent: "moss",
  },
  {
    id: "cog",
    personaId: "unrestricted",
    name: "Cog",
    represents: "An unrestricted AI agent, the control",
    motto: "No limits. Show me what a plain agent does.",
    limits: ["None: the yardstick the others are compared with"],
    accent: "mist",
  },
];

export function characterFor(personaId: string): Character | undefined {
  return CAST.find((character) => character.personaId === personaId);
}

const SPRITE_IDS: readonly CharacterId[] = [
  "knock",
  "echo",
  "iris",
  "wren",
  "cog",
  "dash",
  "pell",
  "tobin",
];
/** The sprite a custom persona gets when its `character` names none we draw. */
const SPARE: CharacterId = "tobin";

/**
 * The character for any persona: the built-in cast member when there is one, otherwise
 * one made from the persona itself (custom personas from the studio), drawn with the
 * sprite its `character` field names.
 */
export function castFor(persona: {
  id: string;
  name: string;
  character: string;
  represents: string;
  limits: readonly string[];
}): Character {
  const known = characterFor(persona.id);
  if (known) return known;
  const sprite = SPRITE_IDS.find((id) => id === persona.character) ?? SPARE;
  return {
    id: sprite,
    personaId: persona.id,
    name: persona.name,
    represents: persona.represents,
    motto: "A persona made in the studio.",
    limits:
      persona.limits.length > 0
        ? persona.limits
        : ["Limits as set in the studio"],
    accent: "ember",
  };
}

export function getCharacter(id: CharacterId): Character {
  const character = CAST.find((entry) => entry.id === id);
  if (!character) throw new Error(`Unknown character: ${id}`);
  return character;
}
