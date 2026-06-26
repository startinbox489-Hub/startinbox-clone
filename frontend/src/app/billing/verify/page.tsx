import { Suspense } from "react";
import { VerificationSkeleton } from "./components/VerificationSkeleton";
import { VerificationContent } from "./components/VerificationContent";
import { IVerifyProps } from "./components/interface";

export default async function VerifyPage({ searchParams }: IVerifyProps) {
  const { status, transaction_id, tx_ref } = await searchParams;
  return (
    <Suspense fallback={<VerificationSkeleton />}>
      <VerificationContent
        status={status}
        transaction_id={transaction_id}
        tx_ref={tx_ref}
      />
    </Suspense>
  );
}
