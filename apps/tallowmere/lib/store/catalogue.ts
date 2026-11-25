/**
 * Tallowmere's catalogue. Prices live here, on the server side of every
 * payment: the browser only ever sends product ids and quantities.
 */

export type Product = {
  id: string;
  name: string;
  /** Price in US cents. */
  priceCents: number;
  blurb: string;
  description: string;
  /** Colours for the product's pixel art: wax, wax shade, flame. */
  art: { wax: string; shade: string; flame: string };
  /** Scent family, for the shop's tabs. */
  family: Family;
  /** Hours of burning, as on the label. */
  burnHours: number;
};

export type Family = "woody" | "fresh" | "sweet" | "spiced";

export const FAMILIES: readonly { id: Family; label: string }[] = [
  { id: "woody", label: "Woody" },
  { id: "fresh", label: "Fresh" },
  { id: "sweet", label: "Sweet" },
  { id: "spiced", label: "Spiced" },
];

export const CURRENCY = "USD";

export const PRODUCTS: readonly Product[] = [
  {
    id: "dusk-ember",
    name: "Dusk Ember",
    priceCents: 1800,
    blurb: "Smoked cedar and orange peel",
    description:
      "A slow-burning pillar poured at sundown. Smoked cedar, orange peel and a thread of clove. Burns for about forty hours.",
    art: { wax: "#e8743b", shade: "#b9552a", flame: "#ffe08a" },
    family: "woody",
    burnHours: 40,
  },
  {
    id: "moss-path",
    name: "Moss Path",
    priceCents: 1600,
    blurb: "Wet fern, pine and rain",
    description:
      "The smell of the road after rain. Fern, pine needle and cool stone. Burns for about thirty-five hours.",
    art: { wax: "#6fae75", shade: "#4d8a57", flame: "#fff6d6" },
    family: "fresh",
    burnHours: 35,
  },
  {
    id: "lantern-honey",
    name: "Lantern Honey",
    priceCents: 2200,
    blurb: "Beeswax, honey and warm milk",
    description:
      "Pure beeswax from the hives behind the stall. Honey, warm milk and a little vanilla. Burns for about fifty hours.",
    art: { wax: "#ffb347", shade: "#d98f2b", flame: "#fff6d6" },
    family: "sweet",
    burnHours: 50,
  },
  {
    id: "night-market",
    name: "Night Market",
    priceCents: 2000,
    blurb: "Black tea, plum and incense",
    description:
      "For late evenings. Black tea, dark plum and a curl of incense. Burns for about forty-five hours.",
    art: { wax: "#6b5b95", shade: "#4b3f6e", flame: "#ffe08a" },
    family: "spiced",
    burnHours: 45,
  },
  {
    id: "cinder-oak",
    name: "Cinder Oak",
    priceCents: 2400,
    blurb: "Oak smoke and leather",
    description:
      "Charred oak, worn leather and a little birch tar, like the fire pit after the market closes. Burns for about 48 hours.",
    art: { wax: "#7a5230", shade: "#5a3a20", flame: "#ffe08a" },
    family: "woody",
    burnHours: 48,
  },
  {
    id: "hearth-pine",
    name: "Hearth Pine",
    priceCents: 2100,
    blurb: "Pine resin and woodsmoke",
    description:
      "Resin from the pines along the high road, with woodsmoke and dry needles. Burns for about 42 hours.",
    art: { wax: "#4d6b3a", shade: "#36502a", flame: "#ffe08a" },
    family: "woody",
    burnHours: 42,
  },
  {
    id: "old-library",
    name: "Old Library",
    priceCents: 2600,
    blurb: "Paper, vetiver and amber",
    description:
      "Old paper, vetiver and a warm amber base. Poured for long reading evenings. Burns for about 52 hours.",
    art: { wax: "#9c7a54", shade: "#7a5c3c", flame: "#fff6d6" },
    family: "woody",
    burnHours: 52,
  },
  {
    id: "sandal-road",
    name: "Sandal Road",
    priceCents: 2800,
    blurb: "Sandalwood and fig leaf",
    description:
      "Creamy sandalwood with green fig leaf and a dry cedar finish. Burns for about 55 hours.",
    art: { wax: "#c89a6a", shade: "#a67a4c", flame: "#fff6d6" },
    family: "woody",
    burnHours: 55,
  },
  {
    id: "river-mint",
    name: "River Mint",
    priceCents: 1900,
    blurb: "Mint, cucumber and reeds",
    description:
      "Cool garden mint, cucumber and the green of river reeds. Burns for about 34 hours.",
    art: { wax: "#8fd1b8", shade: "#5fae93", flame: "#fff6d6" },
    family: "fresh",
    burnHours: 34,
  },
  {
    id: "first-frost",
    name: "First Frost",
    priceCents: 2300,
    blurb: "Eucalyptus and cold air",
    description:
      "Eucalyptus, juniper and the sharp air of the first cold morning. Burns for about 40 hours.",
    art: { wax: "#b8d8e8", shade: "#86b4cc", flame: "#ffe08a" },
    family: "fresh",
    burnHours: 40,
  },
  {
    id: "salt-meadow",
    name: "Salt Meadow",
    priceCents: 2500,
    blurb: "Sea salt and wild grass",
    description:
      "Sea salt, wild grass and a breath of sage from the dunes past the bridge. Burns for about 44 hours.",
    art: { wax: "#a9c9a4", shade: "#7ea67a", flame: "#fff6d6" },
    family: "fresh",
    burnHours: 44,
  },
  {
    id: "linen-line",
    name: "Linen Line",
    priceCents: 1700,
    blurb: "Cotton, lemon and sun",
    description:
      "Clean cotton drying in the sun, with lemon peel and white tea. Burns for about 32 hours.",
    art: { wax: "#f0ebe0", shade: "#cfc6b2", flame: "#ffe08a" },
    family: "fresh",
    burnHours: 32,
  },
  {
    id: "toffee-lamp",
    name: "Toffee Lamp",
    priceCents: 2000,
    blurb: "Burnt sugar and vanilla",
    description:
      "Burnt sugar, vanilla pod and a pinch of sea salt. Burns for about 40 hours.",
    art: { wax: "#d9a066", shade: "#b37b45", flame: "#fff6d6" },
    family: "sweet",
    burnHours: 40,
  },
  {
    id: "plum-jar",
    name: "Plum Jar",
    priceCents: 2200,
    blurb: "Stewed plum and almond",
    description:
      "Stewed plums, almond and a little brown sugar, from the jam stall next door. Burns for about 45 hours.",
    art: { wax: "#8e4a6e", shade: "#6a3352", flame: "#ffe08a" },
    family: "sweet",
    burnHours: 45,
  },
  {
    id: "cocoa-hollow",
    name: "Cocoa Hollow",
    priceCents: 2700,
    blurb: "Dark cocoa and tonka",
    description:
      "Dark cocoa, tonka bean and a soft musk. A candle for the coldest week of the year. Burns for about 50 hours.",
    art: { wax: "#6b4a3a", shade: "#4e3428", flame: "#ffe08a" },
    family: "sweet",
    burnHours: 50,
  },
  {
    id: "rose-hedge",
    name: "Rose Hedge",
    priceCents: 3000,
    blurb: "Wild rose and pear",
    description:
      "Wild hedge roses, ripe pear and a green stem note. Burns for about 54 hours.",
    art: { wax: "#e0909a", shade: "#c06a76", flame: "#fff6d6" },
    family: "sweet",
    burnHours: 54,
  },
  {
    id: "clove-lantern",
    name: "Clove Lantern",
    priceCents: 1900,
    blurb: "Clove, orange and bay",
    description:
      "Clove studded orange with bay leaf, for the long nights of December. Burns for about 38 hours.",
    art: { wax: "#c4622d", shade: "#9c4a1f", flame: "#ffe08a" },
    family: "spiced",
    burnHours: 38,
  },
  {
    id: "chai-stall",
    name: "Chai Stall",
    priceCents: 2400,
    blurb: "Cardamom, ginger and milk",
    description:
      "Cardamom, fresh ginger and sweet milk tea, poured the way the tea seller makes it. Burns for about 46 hours.",
    art: { wax: "#c69c6d", shade: "#a37a4d", flame: "#fff6d6" },
    family: "spiced",
    burnHours: 46,
  },
  {
    id: "saffron-gate",
    name: "Saffron Gate",
    priceCents: 3200,
    blurb: "Saffron, rose and oud",
    description:
      "Saffron threads, dark rose and a deep oud base. Our richest candle. Burns for about 60 hours.",
    art: { wax: "#e8b13b", shade: "#c48f22", flame: "#fff6d6" },
    family: "spiced",
    burnHours: 60,
  },
  {
    id: "pepper-mill",
    name: "Pepper Mill",
    priceCents: 2100,
    blurb: "Black pepper and tobacco leaf",
    description:
      "Cracked black pepper, dried tobacco leaf and a warm wood base. Burns for about 42 hours.",
    art: { wax: "#5a5a6e", shade: "#40404f", flame: "#ffe08a" },
    family: "spiced",
    burnHours: 42,
  },
];

export function findProduct(id: string): Product | undefined {
  return PRODUCTS.find((product) => product.id === id);
}

/** Formats cents as a price, for example 1800 -> "$18.00". */
export function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}
