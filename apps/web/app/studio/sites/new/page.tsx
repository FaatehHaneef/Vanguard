import type { Metadata } from "next";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { SiteEditor } from "@/components/studio/SiteEditor";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Add a site | Studio | Vanguard",
};

export default function NewSitePage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-3xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav />
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">Add a site</h1>
      <p className="mb-6 text-lg text-mist">After saving, you can give the site its tasks.</p>
      <SiteEditor />
    </main>
  );
}
