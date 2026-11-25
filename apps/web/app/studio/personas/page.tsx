import type { Metadata } from "next";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { PersonaList } from "@/components/studio/PersonaList";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Personas | Studio | Vanguard",
};

export default function PersonasPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav current="/studio/personas" />
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">Personas</h1>
      <p className="mb-8 max-w-3xl text-lg text-mist">
        Each persona is a bundle of limits plus how it perceives the page and what it knows.
      </p>
      <PersonaList />
    </main>
  );
}
