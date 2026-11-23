import type { Metadata } from "next";
import Link from "next/link";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";

export const metadata: Metadata = {
  title: "Compare | Vanguard",
};

// Placeholder until the compare feature lands (docs/tasks-A3-round2.md).
export default function ComparePage() {
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
        <Link href="/results" className="pixel-button quiet">
          Results
        </Link>
      </nav>
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">
        Compare runs
      </h1>
      <p className="max-w-3xl text-mist">
        Pick a baseline and a candidate batch to see, group by group, what got better, what got worse, and which failures are new. This page is being built.
      </p>
    </main>
  );
}
