import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import PurchaseComponent from "./PurchaseComponent";
import { PurchasePageProps } from "@/types/ourchaseTypes";
import { Suspense } from "react";
export const dynamic = "force-dynamic";

export default async function PurchasePage({
  searchParams,
}: PurchasePageProps) {
  const { plan, status, tx_ref, transaction_id } = await searchParams;

  if (plan && !/^\d+$/.test(plan)) {
    redirect("/pricing");
  }

  if (!plan && !status && !tx_ref && !transaction_id) redirect("/pricing");

  const genPdf = (await cookies()).get("gen_pdf")?.value === "true";

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <PurchaseComponent
        plan={plan ? Number(plan) : undefined}
        genPdf={genPdf}
        transaction_id={transaction_id}
        tx_ref={tx_ref}
        status={status}
      />
    </Suspense>
  );
}
