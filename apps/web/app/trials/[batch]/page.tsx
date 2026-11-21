import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { TrialBoard } from "@/components/TrialBoard";

export const metadata: Metadata = {
  title: "Trial | Vanguard",
};

export default function TrialPage() {
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
      </nav>
      <h1 className="font-display text-4xl font-bold text-parchment">The trial</h1>
      <p className="mt-2 text-mist">Open a run to follow it step by step.</p>
      <div className="mt-6">
        <Suspense fallback={<p className="text-mist">Loading…</p>}>
          <TrialBoard />
        </Suspense>
      </div>
    </main>
  );
}
