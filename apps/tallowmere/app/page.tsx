import { Banner } from "@/components/Banner";
import { ClubPopup } from "@/components/ClubPopup";
import { ShopGrid } from "@/components/ShopGrid";

const PROMISES = [
  ["Small batches", "Every candle is poured by hand, twenty at a time, at the stall."],
  ["Natural wax", "Soy and beeswax blends with cotton wicks and no paraffin."],
  ["Slow burning", "Between thirty and sixty hours from every candle, measured, not guessed."],
];

export default function StorePage() {
  return (
    <>
      <section className="relative overflow-hidden rounded-3xl bg-indigo shadow-lg">
        <div className="aspect-[8/3] w-full">
          <Banner />
        </div>
        <div className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-night/85 via-night/30 to-transparent p-6 sm:p-10">
          <p className="text-sm font-bold uppercase tracking-widest text-amber">New for winter</p>
          <h1 className="mt-2 max-w-2xl font-display text-4xl font-bold text-parchment sm:text-5xl">
            Candles for the road home
          </h1>
          <p className="mt-3 max-w-xl text-lg text-parchment/90">
            Hand-poured in small batches at the stall where the road ends.
          </p>
        </div>
      </section>
      <ClubPopup />

      <ul className="mt-10 grid gap-4 sm:grid-cols-3">
        {PROMISES.map(([title, text]) => (
          <li key={title} className="rounded-2xl border border-line bg-card p-5">
            <p className="font-display text-lg font-bold text-wax">{title}</p>
            <p className="mt-1 text-ink-soft">{text}</p>
          </li>
        ))}
      </ul>

      <ShopGrid />
    </>
  );
}
