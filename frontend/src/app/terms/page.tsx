import { Suspense } from "react";
import TermsOfService from "./TermsOfService";
export const dynamic = "force-dynamic";

export default function TermsOfServicePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <TermsOfService />
    </Suspense>
  );
}
