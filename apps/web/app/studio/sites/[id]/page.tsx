import type { Metadata } from "next";
import { Suspense } from "react";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { SiteDetailFromRoute } from "@/components/studio/routed";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Site | Studio | Vanguard",
};

export default function SiteStudioPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav />
      <Suspense fallback={<p className="text-mist">Loading…</p>}>
        <SiteDetailFromRoute />
      </Suspense>
    </main>
  );
}
