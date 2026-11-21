import type { Metadata } from "next";
import { Suspense } from "react";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { SitePicker } from "@/components/SitePicker";

export const metadata: Metadata = {
  title: "Choose a site | Vanguard",
};

export default function SitesPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <h1 className="font-display text-4xl font-bold text-parchment sm:text-5xl">
        Where do they go?
      </h1>
      <p className="mt-3 max-w-2xl text-lg text-parchment">
        Pick a site and a task. Every step they take is recorded and checked against their limits.
      </p>
      <div className="mt-6">
        <Suspense fallback={<p className="text-mist">Loading…</p>}>
          <SitePicker />
        </Suspense>
      </div>
    </main>
  );
}
