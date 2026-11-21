import { GameLobby } from "@/components/GameLobby";
import { LobbyBackdrop } from "@/components/LobbyBackdrop";

export default function ArrivalPage() {
  return (
    <main id="main" className="relative isolate mx-auto w-full max-w-6xl flex-1 px-4 py-10">
      <LobbyBackdrop />
      <header className="text-center">
        <p className="font-display text-sm uppercase tracking-[0.3em] text-amber">
          Simulated users, audited
        </p>
        <h1 className="font-display mt-2 text-6xl font-bold text-parchment sm:text-7xl">
          Vanguard
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-xl text-parchment">
          An AI playing a keyboard-only shopper is only useful if it really stays keyboard-only.
          Vanguard checks every step.
        </p>
      </header>
      <div className="mt-4">
        <GameLobby start="circle" />
      </div>
      <p className="mt-10 text-center text-sm text-mist">
        Early, cheap pre-testing. It does not replace testing with disabled people. Trials run only
        on allowed test sites, and payments use a sandbox, so no real money moves.
      </p>
    </main>
  );
}
