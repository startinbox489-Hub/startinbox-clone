"use client";
import { useEffect, useState } from "react";
import { ISearchParams } from "./interface";
import PaymentFailed from "./PaymentFailed";
import { VerificationSkeleton } from "./VerificationSkeleton";
import VerificationSuccess from "./VerificationSuccess";

export function VerificationContent({
  status,
  transaction_id,
  tx_ref,
}: ISearchParams) {
  const [paymentStatus, setPaymentStatus] = useState<"failed" | "success" | "">(
    "",
  );
  const [plan, setPlan] = useState<number>(0);
  const [error, setError] = useState<string>("");
  const [verifyStatus, setVerifyStatus] = useState<string>("");

  useEffect(() => {
    if (status !== "successful") {
      setPaymentStatus("failed");
    }
    const handleVerification = async () => {
      try {
        const response = await fetch("/api/v1/billing/verify", {
          method: "POST",
          credentials: "include",
          body: JSON.stringify({
            payment_reference: transaction_id, // provider ref
            tx_reference: tx_ref, // custom ref
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          if (response.status === 401) {
            console.error("Unathorized");
            setError("Unauthorized");
            setPaymentStatus("failed");
            return;
          }
          console.error(data.message);
          setError(data.message);
          setPaymentStatus("failed");
          return;
        }
        if (data?.status === "not found") {
          setVerifyStatus(data.status);
          setError(data.message);
          setPaymentStatus("failed");
          return;
        }
        if (data?.status === "amount discrepancy") {
          setError(data.message);
          setVerifyStatus(data.status);
          setPaymentStatus("failed");
          return;
        }
        if (data?.status === "failed") {
          setError(data.message);
          setVerifyStatus(data.status);
          setPaymentStatus("failed");
          return;
        }
        setPaymentStatus("success");
        setPlan(data.data.flutterwave_subscription_id);
      } catch (error) {
        console.error((error as Error).message);
        setPaymentStatus("failed");
        return;
      }
    };

    const timer = setTimeout(() => {
      if (status === "successful") {
        handleVerification();
      }
    }, 5_000);
    return () => clearTimeout(timer);
  }, [status, transaction_id, tx_ref]);

  switch (paymentStatus) {
    case "failed":
      return (
        <PaymentFailed
          plan={plan}
          errorMessage={error}
          verifyStatus={verifyStatus}
        />
      );
    case "success":
      return <VerificationSuccess transactionId={`${transaction_id}`} />;
    default:
      return <VerificationSkeleton />;
  }
}
