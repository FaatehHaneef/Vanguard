import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { ComparisonReport } from "@/components/compare/ComparisonReport";

export const metadata: Metadata = {
  title: "Compare | Vanguard",
};

export default function ComparePage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <nav className="mb-6 flex flex-wrap gap-3">
        <Link href="/lobby" className="pixel-button quiet">
          New trial
        </Link>
        <Link href="/trials" className="pixel-button quiet">
          Past trials
        </Link>
        <Link href="/results" className="pixel-button quiet">
          Results
        </Link>
      </nav>
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">Compare runs</h1>
      <p className="mb-6 max-w-3xl text-mist">
        Pick a baseline and a candidate batch to see, group by group, what got better, what got
        worse, and which failures are new. This is how a team sees whether a site change
        introduced new problems.
      </p>
      <Suspense fallback={<p className="text-mist">Loading…</p>}>
        <ComparisonReport />
      </Suspense>
    </main>
  );
}
