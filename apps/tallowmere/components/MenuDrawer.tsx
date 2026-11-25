"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

/** The menu on phone-sized screens: slides in from the right, keeps focus inside, Escape closes. */
export function MenuDrawer({ links }: { links: { href: string; label: string }[] }) {
  const [open, setOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
  const [shownFor, setShownFor] = useState(pathname);

  // Close the drawer when the page changes.
  if (shownFor !== pathname) {
    setShownFor(pathname);
    setOpen(false);
  }

  useEffect(() => {
    if (open) panel.current?.querySelector<HTMLElement>("button, a")?.focus();
  }, [open]);

  function close() {
    setOpen(false);
    button.current?.focus();
  }

  function keepFocus(event: React.KeyboardEvent) {
    if (event.key === "Escape") return close();
    if (event.key !== "Tab" || !panel.current) return;
    const items = panel.current.querySelectorAll<HTMLElement>("button, a");
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  return (
    <>
      <button
        ref={button}
        type="button"
        aria-expanded={open}
        aria-controls="menu-drawer"
        onClick={() => setOpen(true)}
        className="rounded-full border border-line px-4 py-2 font-medium transition-colors duration-150 hover:bg-card"
      >
        Menu
      </button>
      <div
        aria-hidden="true"
        onClick={close}
        className={`fixed inset-0 z-40 bg-ink/50 transition-opacity duration-200 motion-reduce:transition-none ${open ? "opacity-100" : "pointer-events-none opacity-0"}`}
      />
      <div
        ref={panel}
        id="menu-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Menu"
        onKeyDown={keepFocus}
        className={`fixed inset-y-0 right-0 z-50 w-72 max-w-[85vw] bg-paper p-6 shadow-2xl transition-transform duration-200 motion-reduce:transition-none ${open ? "translate-x-0" : "invisible translate-x-full"}`}
      >
        <div className="mb-4 flex items-center justify-between">
          <p className="font-display text-2xl font-bold">Menu</p>
          <button type="button" onClick={close} className="rounded-full border border-line px-4 py-1.5">
            Close
          </button>
        </div>
        <nav aria-label="Main (menu)">
          <ul className="grid gap-1">
            {links.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className="block rounded-lg px-4 py-3 font-medium hover:bg-card">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </>
  );
}
