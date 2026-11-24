"use client";

import { useParams, useSearchParams } from "next/navigation";
import { PersonaEditor } from "./PersonaEditor";
import { SiteDetail } from "./SiteDetail";

/** Read the route here, in the browser, so the pages themselves stay static. */

const param = (value: string | string[] | undefined) =>
  decodeURIComponent(Array.isArray(value) ? value[0] : (value ?? ""));

export function EditPersonaFromRoute() {
  const { id } = useParams<{ id: string }>();
  return <PersonaEditor key={param(id)} personaId={param(id)} />;
}

export function NewPersonaFromRoute() {
  const from = useSearchParams().get("from") || undefined;
  return (
    <>
      <h1 className="mb-6 font-display text-4xl font-bold text-parchment">
        {from ? "Duplicate a persona" : "New persona"}
      </h1>
      <PersonaEditor key={from ?? "blank"} fromId={from} />
    </>
  );
}

export function SiteDetailFromRoute() {
  const { id } = useParams<{ id: string }>();
  return <SiteDetail key={param(id)} siteId={param(id)} />;
}
