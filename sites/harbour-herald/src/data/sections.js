// The paper's sections, in navigation order.
export const sections = [
  { slug: "city", name: "City", blurb: "Councils, transport, housing and the life of the town." },
  { slug: "business", name: "Business", blurb: "The port, local firms, jobs and the high street." },
  { slug: "sport", name: "Sport", blurb: "Harbour Town FC, the rowing club and weekend fixtures." },
  { slug: "culture", name: "Culture", blurb: "Theatre, music, galleries and the people behind them." },
];

export const sectionBySlug = Object.fromEntries(sections.map((s) => [s.slug, s]));
