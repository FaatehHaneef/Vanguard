import type { Metadata } from "next";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { PersonaEditor } from "@/components/studio/PersonaEditor";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Edit persona | Studio | Vanguard",
};

export default async function EditPersonaPage({ params }: PageProps<"/studio/personas/[id]">) {
  const { id } = await params;
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav />
      <h1 className="mb-6 font-display text-4xl font-bold text-parchment">Edit persona</h1>
      <PersonaEditor personaId={decodeURIComponent(id)} />
    </main>
  );
}
