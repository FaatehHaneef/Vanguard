import type { Metadata } from "next";
import Link from "next/link";
import { LabelDesk } from "@/components/LabelDesk";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";

export const metadata: Metadata = {
  title: "Labelling | Vanguard",
};

export default function LabellingPage() {
  return (
    <main
      id="main"
      className="relative isolate mx-auto w-full max-w-5xl flex-1 px-4 py-10"
    >
      <LobbyBackdrop />
      <nav className="mb-6 flex flex-wrap gap-3">
        <Link href="/trials" className="pixel-button quiet">
          Past trials
        </Link>
      </nav>
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">
        Labelling
      </h1>
      <p className="mb-6 max-w-3xl text-mist">
        Judge each step on its own, without discussing it with the other
        labeller. You never see what the checker decided. The rules are in the
        labelling guide (docs/labelling-guide.md).
      </p>
      <LabelDesk />
    </main>
  );
}
