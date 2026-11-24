"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { isCustom, studio, type StudioSite } from "@/lib/studio";

function SiteCard({ site }: { site: StudioSite }) {
  const custom = isCustom(site.id);
  return (
    <li className={`pixel-panel flex flex-col gap-2 ${custom ? "lit" : ""}`}>
      <h3 className="font-display text-2xl font-bold text-parchment">{site.name}</h3>
      <p className="break-all font-mono text-sm text-amber">{site.origin}</p>
      {site.description ? <p className="text-mist">{site.description}</p> : null}
      <p className="text-sm text-mist">{custom ? "Your site" : "Built-in test site, read-only"}</p>
      <Link href={`/studio/sites/${encodeURIComponent(site.id)}`} className="pixel-button mt-auto w-fit">
        {custom ? "Edit the site and its tasks" : "See its tasks, add your own"}
      </Link>
    </li>
  );
}

/** Every site: the built-in test sites and the ones added in the studio. */
export function SiteList() {
  const [sites, setSites] = useState<StudioSite[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    studio
      .allSites()
      .then(setSites)
      .catch((problem: Error) => setError(problem.message));
  }, []);

  if (error) return <p role="alert" className="pixel-panel text-rose">{error}</p>;
  if (!sites) return <p className="text-mist">Loading sites…</p>;
  const custom = sites.filter((site) => isCustom(site.id));
  const builtin = sites.filter((site) => !isCustom(site.id));

  return (
    <div className="grid gap-8">
      <section aria-labelledby="your-sites">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 id="your-sites" className="font-display text-3xl font-bold text-amber">
            Your sites
          </h2>
          <Link href="/studio/sites/new" className="pixel-button">
            Add a site
          </Link>
        </div>
        {custom.length ? (
          <ul className="grid gap-5 md:grid-cols-2">
            {custom.map((site) => (
              <SiteCard key={site.id} site={site} />
            ))}
          </ul>
        ) : (
          <p className="pixel-panel text-mist">
            No sites yet. Add a site you own or are allowed to test, then give it tasks.
          </p>
        )}
      </section>
      <section aria-labelledby="test-sites">
        <h2 id="test-sites" className="mb-4 font-display text-3xl font-bold text-amber">
          Built-in test sites
        </h2>
        <ul className="grid gap-5 md:grid-cols-2">
          {builtin.map((site) => (
            <SiteCard key={site.id} site={site} />
          ))}
        </ul>
      </section>
    </div>
  );
}
