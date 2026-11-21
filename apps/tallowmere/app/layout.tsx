import type { Metadata } from "next";
import { Atkinson_Hyperlegible, Pixelify_Sans } from "next/font/google";
import Link from "next/link";
import { CartLink } from "@/components/CartLink";
import "./globals.css";

const body = Atkinson_Hyperlegible({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "700"],
});

const pixel = Pixelify_Sans({
  variable: "--font-pixel",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "Tallowmere Candles",
  description: "Hand-poured candles from the stall at the end of the road.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${body.variable} ${pixel.variable} h-full antialiased`}>
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
          <header className="border-b border-line">
            <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-4">
              <Link href="/" className="font-display text-3xl font-bold text-wax">
                Tallowmere
              </Link>
              <nav className="flex items-center gap-5">
                <Link href="/" className="text-ink underline-offset-4 hover:underline">
                  Candles
                </Link>
                <CartLink />
              </nav>
            </div>
          </header>
          <main id="main" className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
            {children}
          </main>
          <footer className="border-t border-line px-4 py-6 text-center text-sm text-ink-soft">
            Tallowmere is a fictional shop built to be tested.
            {/*
              Planted for the trials: far from where any page opens, so someone using a
              screen magnifier only knows it after moving their view down here.
            */}
            <span className="block">Shop reference WICK-0094</span>
          </footer>
        </div>
      </body>
    </html>
  );
}
