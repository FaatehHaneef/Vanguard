"use client";

import { useEffect, useState } from "react";
import { isCustom, studio, type StudioSite } from "@/lib/studio";
import { SiteEditor } from "./SiteEditor";
import { TaskManager } from "./TaskManager";

/** One site: its editor (custom sites) or its details (built-in sites, read-only). */
export function SiteDetail({ siteId }: { siteId: string }) {
  const [site, setSite] = useState<StudioSite | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    studio
      .site(siteId)
      .then(setSite)
      .catch((problem: Error) => setError(problem.message));
  }, [siteId]);

  if (error) return <p role="alert" className="pixel-panel text-rose">{error}</p>;
  if (!site) return <p className="text-mist">Loading…</p>;

  return (
    <div className="grid gap-8">
      <section aria-labelledby="site-title">
        <h1 id="site-title" className="mb-2 font-display text-4xl font-bold text-parchment">
          {site.name}
        </h1>
        <p className="mb-6 break-all font-mono text-amber">{site.origin}</p>
        {isCustom(site.id) ? (
          <SiteEditor site={site} onSaved={setSite} />
        ) : (
          <div className="pixel-panel text-parchment">
            <p>{site.description}</p>
            <p className="mt-3 text-sm text-mist">
              A built-in test site: read-only. You can still add your own tasks to it below.
            </p>
          </div>
        )}
      </section>
      <TaskManager siteId={site.id} />
    </div>
  );
}
