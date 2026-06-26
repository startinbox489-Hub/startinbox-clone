import { Suspense } from "react";
import PaymentVerification from "./components/PaymentVerification";
import { VerificationSkeleton } from "../billing/verify/components/VerificationSkeleton";
export const dynamic = "force-dynamic";

export default function CheckoutPage() {
  return (
    <Suspense fallback={<VerificationSkeleton />}>
      <PaymentVerification />
    </Suspense>
  );
}
