import { Suspense } from "react";
import { OrderView } from "@/components/OrderView";

export default function ThanksPage() {
  return (
    <Suspense fallback={<p className="text-lg">Fetching your order…</p>}>
      <OrderView />
    </Suspense>
  );
}
