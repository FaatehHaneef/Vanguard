import type { Metadata } from "next";
import Link from "next/link";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";
import { StudioNav } from "@/components/studio/StudioNav";

export const metadata: Metadata = {
  title: "Studio | Vanguard",
};

const AREAS = [
  {
    href: "/studio/personas",
    title: "Personas",
    body: "Make your own simulated users: who they are, what they cannot do, how they perceive the page and what they already know. Start from scratch or duplicate one of the built-in cast.",
    action: "Open personas",
  },
  {
    href: "/studio/sites",
    title: "Sites and tasks",
    body: "Add a website you own or are allowed to test, then give it tasks: where to start, what to do and how Vanguard knows the task was done.",
    action: "Open sites and tasks",
  },
];

export default function StudioPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <StudioNav current="/studio" />
      <h1 className="mb-2 font-display text-4xl font-bold text-parchment">Configuration studio</h1>
      <p className="mb-8 max-w-3xl text-lg text-mist">
        Create and save your own personas, add any website and define its tasks, without changing
        code. Everything you save here appears at once in the lobby&rsquo;s site picker, in trials and
        in the results, next to the built-in cast and sites.
      </p>
      <ul className="grid gap-6 md:grid-cols-2">
        {AREAS.map((area) => (
          <li key={area.href} className="pixel-panel flex flex-col gap-4">
            <h2 className="font-display text-3xl font-bold text-amber">{area.title}</h2>
            <p className="flex-1 text-parchment">{area.body}</p>
            <Link href={area.href} className="pixel-button w-fit">
              {area.action}
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-8 max-w-3xl text-sm text-mist">
        Built-in personas, sites and tasks are read-only. A persona you make counts as a full
        persona only when it applies its limits exactly as a validated built-in persona does;
        otherwise it is a preview persona, whose limits are stated to the model but not enforced,
        and its trials run prompt-only.
      </p>
    </main>
  );
}
