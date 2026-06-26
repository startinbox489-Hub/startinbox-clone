"use client";

export const dynamic = "force-dynamic";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import usePlansStoreState from "@/store/planStore";

import { PaymentUtil } from "../util";
import StatusCase from "./StatusCase";
import { TempIdeaT } from "@/components/Landing/ValidateIdeaSection/interface";

const MAX_RETRIES = 3;
const RETRY_INTERVAL_MS = 8000;

export default function PaymentVerification() {
  const setSelectedPlan = usePlansStoreState((s) => s.setSelectedPlan);
  const router = useRouter();
  const searchParams = useSearchParams();

  const [transactionDetails, setTransactionDetails] = useState({
    status: searchParams?.get("status"),
    tx_ref: searchParams?.get("tx_ref"), // flw & stripe
    transaction_id: searchParams?.get("transaction_id"), // flw
    success: searchParams?.get("success"), // stripe
    canceled: searchParams?.get("canceled"), // stripe
    trxref: searchParams?.get("trxref"), // paystack
    reference: searchParams?.get("reference"), // paystack
  });

  const [verificationStatus, setVerificationStatus] = useState("loading");
  const [message, setMessage] = useState(
    "Verifying your payment, please wait...",
  );
  const [retryCount, setRetryCount] = useState(0);

  const handleVerification = useCallback(async () => {
    let provider = "";
    let paymentIdentifier = "";

    // +++++++++++++ Determine Payment Provider and Identifier ++++++++++++++
    if (transactionDetails.status === "session_expired") {
      setVerificationStatus("Payment Session expired");
      setMessage("Payment Session has expired. Took too long to make payment.");
      console.log(
        "Payment Session has expired. Took too long to make payment.",
      );
      setVerificationStatus("session_expired");
      return;
    } else if (
      transactionDetails.status === "cancelled" &&
      transactionDetails.tx_ref
    ) {
      provider = "flutterwave";
      setMessage("Payment Cancelled Successfully.");
      console.log("Payment Cancelled Successfully.");
      setVerificationStatus("cancelled");
      return;
    } else if (
      transactionDetails.transaction_id &&
      transactionDetails.status &&
      transactionDetails.tx_ref
    ) {
      // Flutterwave
      provider = "flutterwave";
      paymentIdentifier =
        transactionDetails.transaction_id || transactionDetails.tx_ref;
      setMessage("Verifying Flutterwave payment...");
      console.log("Verifying Flutterwave payment...");
    } else if (
      transactionDetails.tx_ref &&
      (transactionDetails.success || transactionDetails.canceled)
    ) {
      // Stripe
      provider = "stripe";
      paymentIdentifier = transactionDetails.tx_ref as string;
      setMessage("Verifying Stripe payment...");
      console.log("Verifying Stripe payment...");
    } else if (transactionDetails.trxref && transactionDetails.reference) {
      // Stripe
      provider = "paystack";
      paymentIdentifier = transactionDetails.reference as string;
      setMessage("Verifying Paystack payment...");
      console.log("Verifying Paystack payment...");
    } else {
      setVerificationStatus("failed");
      setMessage(
        "Payment details not found. Please ensure you clicked the link correctly or contact support.",
      );
      console.log(
        "Payment details not found. Please ensure you clicked the link correctly or contact support.",
      );
      return;
    }

    // +++++++++++++++ Status Check (Initial assessment) ++++++++++++++++
    if (
      transactionDetails.tx_ref ||
      (transactionDetails.trxref &&
        (transactionDetails.status === "successful" ||
          transactionDetails.canceled === "true" ||
          transactionDetails.success === "true" ||
          transactionDetails.reference))
    ) {
      setVerificationStatus("loading");
      setMessage(
        `Payment processed on ${provider}. Finalizing verification...`,
      );
      console.log(
        `Payment processed on ${provider}. Finalizing verification...`,
      );

      const paymentVerifyResponse = await PaymentUtil.sendVerificationToBackend(
        provider,
        paymentIdentifier,
        transactionDetails.tx_ref
          ? transactionDetails.tx_ref
          : (transactionDetails.trxref as string),
      );
      // console.log('payment paymentVerifyResponse: ', paymentVerifyResponse);

      const backendStatus = paymentVerifyResponse?.data?.status || "failed";

      if (
        ["success", "paid", "approved", "successful"].includes(backendStatus)
      ) {
        // >>>>>>>> success <<<<<<<<<<<<<<
        setVerificationStatus("success");
        setMessage(
          paymentVerifyResponse.message || "Payment successfully verified!",
        );
        console.log(
          paymentVerifyResponse.message || "Payment successfully verified!",
        );
        setSelectedPlan(
          paymentVerifyResponse.data.subscription_plan_idx as number,
        );
        // make a new request to validate idea and then redirect to analysis
        const tempIdea: TempIdeaT | undefined | null =
          PaymentUtil.getFromLocalStorage("tempIdea");
        console.log("tempIdea tempIdea: ", tempIdea);
        if (tempIdea?.tempIdea) {
          const ideaResponseData = await PaymentUtil.sendIdeaToBackend(
            paymentVerifyResponse.data.subscription_plan_id as string,
            tempIdea.tempIdea,
          );
          if (ideaResponseData?.idea) {
            PaymentUtil.saveToLocalStorage("ideaReply", {
              preview: ideaResponseData?.idea?.idea_validation,
              ideaScore: ideaResponseData?.idea?.idea_score,
              prompt: ideaResponseData?.idea?.prompt,
              id: ideaResponseData?.idea?.id,
              sentReview: false,
            });
          } else {
            if (ideaResponseData.message.startsWith("Payment is required")) {
              setMessage(
                "Subscription already used. Redirecting back to Idea validation...",
              );
              console.log(
                "Subscription already used. Redirecting back to Idea validation...",
              );
              router.push("/");
              return;
            }
          }
          PaymentUtil.removeFromLocalStorage("pending_transaction");
          PaymentUtil.removeFromLocalStorage("IsConsulted");
          router.push("/analysis"); // Redirect on success with propmt reply
          return;
        } else {
          router.push("/"); // Redirect back for prompting
          return;
        }
      } else if (paymentVerifyResponse.status === "amount discrepancy") {
        setVerificationStatus("amount discrepancy");
        setMessage(
          `${paymentVerifyResponse.message}. If you believe this is a mistake, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}`,
        );
        console.log(
          `${paymentVerifyResponse.message}. If you believe this is a mistake, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}`,
        );
        return;
      } else if (backendStatus === "not found") {
        // >>>>>>>> not found <<<<<<<<<<<<<<
        setVerificationStatus("not found");
        setMessage("Payment was not found.");
        console.log("Payment was not found.");
        PaymentUtil.removeFromLocalStorage("pending_transaction");
        router.push("/#pricing");
      } else if (paymentVerifyResponse.status === "signin required") {
        // >>>>>>>> signin required <<<<<<<
        setVerificationStatus("signin required");
        setMessage("signin required");
        console.log("signin required");
        // save pending transactions
        PaymentUtil.saveToLocalStorage("pending_transaction", {
          txReference: transactionDetails.transaction_id,
          paymentReference: transactionDetails.tx_ref,
          status: transactionDetails.status,
          success: transactionDetails.success,
          canceled: transactionDetails.canceled,
          trxref: transactionDetails.trxref,
          reference: transactionDetails.reference,
        });
        router.push("/signin");
      } else if (paymentVerifyResponse.message === "Internal Server Error") {
        setVerificationStatus("Unexpected Error");
        setMessage(
          `Something went wrong. Could not complete process, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}`,
        );
        console.log(
          `Something went wrong. Could not complete process, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}`,
        );
      } else if (backendStatus === "pending") {
        // >>>>>>>> pending <<<<<<<<<<<<<<
        setVerificationStatus("pending");
        setMessage(
          "Payment is still pending verification. Please wait, we are rechecking...",
        );
        console.log(
          "Payment is still pending verification. Please wait, we are rechecking...",
        );
        if (retryCount < MAX_RETRIES) {
          setTimeout(
            () => setRetryCount((prev) => prev + 1),
            RETRY_INTERVAL_MS,
          );
        } else {
          setVerificationStatus("failed");
          setMessage(
            `Payment verification timed out after multiple retries. If you believe this is a mistake, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}.`,
          );
          console.log(
            `Payment verification timed out after multiple retries. If you believe this is a mistake, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}.`,
          );
        }
      } else {
        // >>>>>>>> all else <<<<<<<<<<<<<<
        setVerificationStatus("failed");
        setMessage(
          `Payment verification failed. If you believe this is a mistake, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}`,
        );
        console.log(
          `Payment verification failed. If you believe this is a mistake, please contact our help center with your transaction reference: ${transactionDetails.tx_ref}`,
        );
        PaymentUtil.removeFromLocalStorage("pending_transaction");
      }
    } else if (
      transactionDetails.status === "pending" ||
      transactionDetails.success === "pending" ||
      transactionDetails.canceled === "pending"
    ) {
      setVerificationStatus("pending");
      setMessage(
        "Your payment is currently pending. We are re-checking the status...",
      );
      console.log(
        "Your payment is currently pending. We are re-checking the status...",
      );
      if (retryCount < MAX_RETRIES) {
        setTimeout(() => setRetryCount((prev) => prev + 1), RETRY_INTERVAL_MS);
      } else {
        setVerificationStatus("failed");
        setMessage(
          `Payment verification timed out after multiple retries. If you believe this is a mistake, please contact our help center with your transaction reference ${transactionDetails.tx_ref}.`,
        );
        console.log(
          `Payment verification timed out after multiple retries. If you believe this is a mistake, please contact our help center with your transaction reference ${transactionDetails.tx_ref}.`,
        );
        PaymentUtil.removeFromLocalStorage("pending_transaction");
      }
    } else {
      // 'failed', 'cancelled', or other error statuses
      setVerificationStatus("failed");
      setMessage(
        `Payment was not successful. Status: ${
          transactionDetails.status ||
          transactionDetails.canceled ||
          transactionDetails.success
        }. If you think this is an error, please contact our help center.`,
      );
      PaymentUtil.removeFromLocalStorage("pending_transaction");
    }
  }, [transactionDetails, retryCount, setSelectedPlan, router]);

  useEffect(() => {
    const userData = localStorage.getItem("userData");
    if (!userData || userData === null) {
      router.push("/signin");
      return;
    }
  }, [router]);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (transactionDetails) {
      timer = setTimeout(() => handleVerification(), RETRY_INTERVAL_MS);
    }

    return () => {
      clearTimeout(timer);
    };
  }, [transactionDetails, retryCount, handleVerification]);

  useEffect(() => {
    const pendingTx = PaymentUtil.getFromLocalStorage("pending_transaction");
    if (pendingTx) {
      const {
        txReference,
        paymentReference,
        status,
        success,
        canceled,
        reference,
        trxref,
      } = pendingTx;
      setRetryCount(0);
      setTransactionDetails({
        transaction_id: txReference,
        tx_ref: paymentReference,
        status,
        success,
        canceled,
        reference,
        trxref,
      });
    }
  }, []);

  const renderContent = () => {
    switch (verificationStatus) {
      case "loading":
        return (
          <StatusCase
            status="loading"
            title="Processing..."
            message={message}
          />
        );
      case "session_expired":
        return (
          <StatusCase
            status="loading"
            title="Session Expired"
            message={message}
            action={
              <button
                onClick={() => router.push("/")}
                className="px-4 py-2 bg-red-600 text-white rounded"
              >
                Return to Idea Validation
              </button>
            }
          />
        );
      case "pending":
        return (
          <StatusCase
            status="pending"
            title="Payment Pending"
            message={message}
            action={
              <p className="text-sm text-gray-500">
                Retrying ({retryCount})...
              </p>
            }
          />
        );
      case "success":
        return (
          <StatusCase
            status="success"
            title="Payment Confirmed!"
            message={message}
            action={<p className="text-sm text-gray-500">Redirecting you…</p>}
          />
        );
      case "failed":
        return (
          <StatusCase
            status="failed"
            title="Payment Failed"
            message={message}
            action={
              <button
                onClick={() => router.push("/plans")}
                className="px-4 py-2 bg-red-600 text-white rounded"
              >
                Retry Payment
              </button>
            }
          />
        );
      case "cancelled":
        return (
          <StatusCase
            status="cancelled"
            title="Payment Cancelled"
            message={message}
            action={
              <button
                onClick={() => router.push("/")}
                className="px-4 py-2 bg-red-600 text-white rounded"
              >
                Back
              </button>
            }
          />
        );
      case "not found":
        return (
          <StatusCase
            status="notfound"
            title="Transaction Not Found"
            message={message}
          />
        );
      case "signin required":
        return (
          <StatusCase
            status="signin"
            title="Sign in Required"
            message={message}
            action={
              <button
                onClick={() => router.push("/signin")}
                className="px-4 py-2 bg-indigo-600 text-white rounded"
              >
                Sign In
              </button>
            }
          />
        );
      case "amount discrepancy":
        return (
          <StatusCase
            status="amount"
            title="Amount Discrepancy"
            message={message}
            action={
              <button
                onClick={() => router.push("/support")}
                className="px-4 py-2 bg-orange-600 text-white rounded"
              >
                Contact Support
              </button>
            }
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md text-center">
        {renderContent()}
      </div>
    </div>
  );
}
