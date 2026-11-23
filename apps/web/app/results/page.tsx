import type { Metadata } from "next";
import Link from "next/link";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { ResultsDashboard } from "@/components/ResultsDashboard";

export const metadata: Metadata = {
  title: "Results | Vanguard",
};

export default function ResultsPage() {
  return (
    <main
      id="main"
      className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10"
    >
      <LobbyBackdrop />
      <nav className="mb-6 flex flex-wrap gap-3">
        <Link href="/lobby" className="pixel-button quiet">
          New trial
        </Link>
        <Link href="/trials" className="pixel-button quiet">
          Past trials
        </Link>
        <Link href="/labelling" className="pixel-button quiet">
          Labelling
        </Link>
        <Link href="/compare" className="pixel-button quiet">
          Compare
        </Link>
        <Link href="/studio" className="pixel-button quiet">
          Studio
        </Link>
      </nav>
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">
        Results
      </h1>
      <p className="mb-6 max-w-3xl text-mist">
        Every number here is computed by code from the recorded steps: the
        leakage checker uses the same rules as the gate, and no model counts,
        scores or judges anything.
      </p>
      <ResultsDashboard />
    </main>
  );
}
