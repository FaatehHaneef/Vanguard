import Link from "next/link";

const LINKS = [
  { href: "/studio", label: "Studio" },
  { href: "/studio/personas", label: "Personas" },
  { href: "/studio/sites", label: "Sites and tasks" },
  { href: "/lobby", label: "New trial" },
  { href: "/results", label: "Results" },
];

/** The row of links at the top of every studio page. */
export function StudioNav({ current }: { current?: string }) {
  return (
    <nav aria-label="Studio" className="mb-6 flex flex-wrap gap-3">
      {LINKS.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className="pixel-button quiet"
          aria-current={current === link.href ? "page" : undefined}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
}
