import type { Metadata } from "next";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { SiteDetail } from "@/components/studio/SiteDetail";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Site | Studio | Vanguard",
};

export default async function SiteStudioPage({ params }: PageProps<"/studio/sites/[id]">) {
  const { id } = await params;
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-5xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav />
      <SiteDetail siteId={decodeURIComponent(id)} />
    </main>
  );
}
