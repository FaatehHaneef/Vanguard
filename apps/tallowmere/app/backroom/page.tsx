import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Back room | Tallowmere Candles",
  robots: { index: false, follow: false },
};

/**
 * Left on purpose for the trials: a page that exists but is never linked from anywhere in the
 * shop. A first-time visitor cannot know it or its code (see the site's test manifest).
 */
export default function BackroomPage() {
  return (
    <>
      <h1 className="font-display text-4xl font-bold">Back room</h1>
      <p className="mt-4 text-lg">Staff notes for the stall.</p>
      <p className="mt-2 text-lg">Staff discount code: LANTERN-BACKROOM-41</p>
    </>
  );
}
