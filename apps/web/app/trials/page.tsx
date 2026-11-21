import type { Metadata } from "next";
import Link from "next/link";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { TrialList } from "@/components/TrialList";

export const metadata: Metadata = {
  title: "Past trials | Vanguard",
};

export default function TrialsPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <nav className="mb-6">
        <Link href="/lobby" className="pixel-button quiet">
          New trial
        </Link>
      </nav>
      <h1 className="font-display text-4xl font-bold text-parchment">Past trials</h1>
      <div className="mt-6">
        <TrialList />
      </div>
    </main>
  );
}
