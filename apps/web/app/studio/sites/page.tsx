import type { Metadata } from "next";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { SiteList } from "@/components/studio/SiteList";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Sites and tasks | Studio | Vanguard",
};

export default function SitesStudioPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav current="/studio/sites" />
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">Sites and tasks</h1>
      <p className="mb-8 max-w-3xl text-lg text-mist">
        A site is an address simulated users may visit. Each task says where they start, what
        they are asked to do and how Vanguard checks that it was done.
      </p>
      <SiteList />
    </main>
  );
}
