import type { Metadata } from "next";
import { GameLobby } from "@/components/GameLobby";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";

export const metadata: Metadata = {
  title: "The simulated users | Vanguard",
};

export default function LobbyPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <h1 className="font-display text-4xl font-bold text-parchment sm:text-5xl">
        Choose your simulated users
      </h1>
      <p className="mt-3 max-w-2xl text-lg text-parchment">
        Each one lives with real limits: what they can perceive, how they can act, what they know.
        Pick who goes, then choose where they go.
      </p>
      <div className="mt-6">
        <GameLobby start="line" />
      </div>
    </main>
  );
}
