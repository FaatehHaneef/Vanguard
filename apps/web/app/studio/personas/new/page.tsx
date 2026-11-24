import type { Metadata } from "next";
import { Suspense } from "react";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { NewPersonaFromRoute } from "@/components/studio/routed";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "New persona | Studio | Vanguard",
};

export default function NewPersonaPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav />
      <Suspense fallback={<p className="text-mist">Loading…</p>}>
        <NewPersonaFromRoute />
      </Suspense>
    </main>
  );
}
