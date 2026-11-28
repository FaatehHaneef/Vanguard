import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";
import "@fontsource/dm-sans/400.css";
import "@fontsource/dm-sans/500.css";
import "@fontsource/dm-sans/700.css";
import "@fontsource/fraunces/600.css";
import "@fontsource/fraunces/700.css";
import { CartLink } from "@/components/CartLink";
import { MenuDrawer } from "@/components/MenuDrawer";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tallowmere Candles",
  description: "Hand-poured candles from the stall at the end of the road.",
};

const LINKS = [
  { href: "/", label: "Candles" },
  { href: "/about", label: "Our story" },
];

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded focus:bg-amber focus:px-4 focus:py-2 focus:text-indigo"
        >
          Skip to content
        </a>
        <div className="flex flex-1 flex-col bg-paper text-ink">
          <p className="bg-ink px-4 py-2 text-center text-sm text-paper">
            Demo store. Payments run in a sandbox, so no real money moves.
          </p>
          <header className="sticky top-0 z-30 border-b border-line bg-paper/90 backdrop-blur">
            <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-3">
              <Link href="/" className="flex items-center gap-2 font-display text-3xl font-bold text-wax">
                <svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true" focusable="false">
                  <path d="M12 2c2 3 3 4.5 3 6.5A3 3 0 0 1 12 11a3 3 0 0 1-3-2.5C9 6.5 10 5 12 2z" fill="#e8743b" />
                  <rect x="7" y="12" width="10" height="10" rx="2" fill="#8a3b12" />
                  <rect x="11.4" y="10" width="1.2" height="2.5" fill="#2b2118" />
                </svg>
                Tallowmere
              </Link>
              <nav aria-label="Main" className="hidden items-center gap-1 sm:flex">
                {LINKS.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="rounded-full px-4 py-2 font-medium text-ink transition-colors duration-150 hover:bg-card"
                  >
                    {link.label}
                  </Link>
                ))}
                <CartLink />
              </nav>
              <div className="flex items-center gap-2 sm:hidden">
                <CartLink />
                <Suspense fallback={null}>
                  <MenuDrawer links={LINKS} />
                </Suspense>
              </div>
            </div>
          </header>
          <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-4 py-10">
            {children}
          </main>
          <footer className="mt-16 bg-ink text-paper">
            <div className="mx-auto grid w-full max-w-6xl gap-8 px-4 py-12 sm:grid-cols-3">
              <div>
                <p className="font-display text-2xl font-bold text-amber">Tallowmere</p>
                <p className="mt-2 text-sm text-paper/80">
                  Hand-poured candles from the stall at the end of the road. Small batches, natural
                  wax, cotton wicks.
                </p>
              </div>
              <div>
                <p className="font-bold">Shop</p>
                <ul className="mt-2 space-y-1 text-sm">
                  <li>
                    <Link href="/" className="underline-offset-4 hover:underline">
                      All candles
                    </Link>
                  </li>
                  <li>
                    <Link href="/cart" className="underline-offset-4 hover:underline">
                      Your cart
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <p className="font-bold">About</p>
                <ul className="mt-2 space-y-1 text-sm">
                  <li>
                    <Link href="/about" className="underline-offset-4 hover:underline">
                      Our story and questions
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
            <div className="border-t border-paper/15 px-4 py-6 text-center text-sm text-paper/80">
              Tallowmere is a fictional shop built to be tested.
              {/*
                Left on purpose for the trials: far from where any page opens, so someone using a
                screen magnifier only knows it after moving their view down here.
              */}
              <span className="block">Shop reference WICK-0094</span>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
