import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { RunFeed } from "@/components/RunFeed";

export const metadata: Metadata = {
  title: "Run | Vanguard",
};

export default function RunPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <nav className="mb-6 flex flex-wrap gap-3">
        <Link href="/trials" className="pixel-button quiet">
          Past trials
        </Link>
        <Link href="/lobby" className="pixel-button quiet">
          New trial
        </Link>
      </nav>
      <Suspense fallback={<p className="text-mist">Loading…</p>}>
        <RunFeed />
      </Suspense>
    </main>
  );
}
