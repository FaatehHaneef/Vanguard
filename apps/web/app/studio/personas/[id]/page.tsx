import type { Metadata } from "next";
import { Suspense } from "react";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { EditPersonaFromRoute } from "@/components/studio/routed";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Edit persona | Studio | Vanguard",
};

export default function EditPersonaPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav />
      <h1 className="mb-6 font-display text-4xl font-bold text-parchment">Edit persona</h1>
      <Suspense fallback={<p className="text-mist">Loading…</p>}>
        <EditPersonaFromRoute />
      </Suspense>
    </main>
  );
}
