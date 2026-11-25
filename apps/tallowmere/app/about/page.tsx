import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Our story | Tallowmere Candles" };

const QUESTIONS = [
  [
    "How long does delivery take?",
    "Orders placed by 3pm leave the stall the same day. Most arrive in two to three working days. Delivery is free on orders over $40.",
  ],
  [
    "Can I return a candle?",
    "Unlit candles can be returned within 30 days for a full refund. If a candle arrives damaged, tell us within a week and we will send another.",
  ],
  [
    "Why did my candle tunnel?",
    "Tunnelling happens when the first burn is too short. Burn a new candle until the melted wax reaches the edge of the jar, about two hours.",
  ],
  [
    "Do you make candles to order?",
    "Yes, for orders of twenty or more. Write to us with the scent and the date you need them, and we will reply within two working days.",
  ],
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <p className="text-sm font-bold uppercase tracking-widest text-wax">Our story</p>
      <h1 className="mt-2 font-display text-4xl font-bold">A stall at the end of the road</h1>
      <p className="mt-4 text-lg text-ink-soft">
        Tallowmere started in 2019 as a single table at the night market, selling twelve candles
        a week. We still pour every candle by hand at the same stall, in batches of twenty, with
        wax from the hives behind it and scents we mix ourselves.
      </p>
      <p className="mt-4 text-lg text-ink-soft">
        Every candle is tested for at least thirty hours before a scent goes on sale, and the
        burn time on each label is the time we measured, not a guess.
      </p>

      <h2 className="mt-12 font-display text-3xl font-bold">Common questions</h2>
      <div className="mt-4 divide-y divide-line overflow-hidden rounded-2xl border border-line bg-card">
        {QUESTIONS.map(([question, answer]) => (
          <details key={question} className="group">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 font-bold transition-colors duration-150 hover:bg-paper [&::-webkit-details-marker]:hidden">
              {question}
              <span
                aria-hidden="true"
                className="h-2.5 w-2.5 flex-none rotate-45 border-b-2 border-r-2 border-wax transition-transform duration-200 group-open:rotate-[225deg]"
              />
            </summary>
            <p className="rise px-5 pb-4 text-ink-soft">{answer}</p>
          </details>
        ))}
      </div>

      <p className="mt-10">
        <Link href="/" className="rounded-full bg-wax px-6 py-3 font-bold text-card transition-colors duration-150 hover:bg-ink">
          Browse the candles
        </Link>
      </p>
    </div>
  );
}
