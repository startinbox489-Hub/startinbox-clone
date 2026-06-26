"use client";

import CustomCookieUtil from "@/lib/client/setCookie";
import {
  ApiInitiatePayResponseI,
  ApiVerifyPayResponseI,
} from "@/types/paymentVerification.types";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import StatusProgress from "./StatusProgress";
import { PurchaseComponentProps, ResultState } from "@/types/ourchaseTypes";
import { RETRY_CONFIG, UI_MAP } from "./util";

const PurchaseComponent: React.FC<PurchaseComponentProps> = ({
  plan,
  genPdf,
  tx_ref,
  transaction_id,
  status,
}) => {
  const router = useRouter();

  const [retryCount, setRetryCount] = useState(0);
  const [progress, setProgress] = useState<number>(20);
  const retryTimerRef = useRef<NodeJS.Timeout | null>(null);

  const [message, setMessage] = useState<string>("");
  const [resStatus, setResStatus] = useState<ResultState>("processing");

  // Prevent duplicate intent creation on re-render
  const paymentIntentStarted = useRef(false);

  const animateProgress = (from: number, to: number, durationMs: number) => {
    const start = performance.now();

    const tick = (now: number) => {
      const elapsed = Math.min((now - start) / durationMs, 1);
      const value = from + (to - from) * elapsed;
      setProgress(Math.round(value));

      if (elapsed < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  };

  // Create payment intent and redirect user to Flutterwave
  // Runs ONLY when plan is present (initial checkout).
  useEffect(() => {
    if (!plan || paymentIntentStarted.current) return;

    const getPaymentIntent = async () => {
      paymentIntentStarted.current = true;

      try {
        const response = await fetch("/api/v1/payments", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            subscription_plan_idx: plan,
            gen_pdf: genPdf,
            to_purchase: "true", // enables redirect to checkout/purchase and not /checkout
          }),
        });

        if ([201, 200].includes(response.status)) {
          const data: ApiInitiatePayResponseI = await response.json();
          if (data.data.has_active_payment) {
            setResStatus("active_payment_detected");
            setMessage(data.message);
            const ideaReply = localStorage.getItem("ideaReply");
            const parsedIdeaReply = ideaReply ? JSON.parse(ideaReply) : null;
            if (parsedIdeaReply && parsedIdeaReply.id) {
              const ideaId = parsedIdeaReply.id;

              const res = await fetch(`/api/v1/startup-ideas/${ideaId}`, {
                method: "GET",
                credentials: "include",
              });
              if (res.ok) {
                const ideaReply = (await res.json()).data;
                localStorage.setItem(
                  "ideaReply",
                  JSON.stringify({
                    preview: ideaReply.idea_validation,
                    ideaScore: ideaReply.idea_score,
                    prompt: ideaReply.prompt,
                    id: ideaReply.id,
                    sentReview: parsedIdeaReply.sentReview,
                    idx: parsedIdeaReply.idx,
                    canceledPay: true,
                  }),
                );
              }
            }
            router.push("/analysis");
            return;
          }
          const paymentLink: string | undefined = data?.data?.payment_link;
          setResStatus("redirecting");
          if (paymentLink) {
            router.push(paymentLink);
            return;
          }
        } else if (response.status === 401) {
          router.replace(
            `/signin?next=${encodeURI(`/checkout/purchase?plan=${plan}`)}`,
          );
          return;
        } else if (response.status === 404) {
          setResStatus("not_found");
          setMessage("Invalid Subscription Plan");
          return;
        } else if (response.status === 409) {
          const data: ApiInitiatePayResponseI = await response.json();
          setResStatus("adds_on_error");
          setMessage(data.message);
          return;
        } else if (response.status > 499) {
          setResStatus("server_error");
          setMessage(
            "An Unexpected Error Occurred. Unable to initialize payment. Please contact support with: PAY#002",
          );
          return;
        }
      } catch (error) {
        console.error("Payment intent error:", error);
        setResStatus("server_error");
        setMessage("Unexpected error initializing payment. PAY#003");
      }
    };

    getPaymentIntent();
  }, [plan, genPdf, router]);

  // Verify payment after redirect back from provider
  useEffect(() => {
    if (status === "cancelled") {
      setResStatus("cancelled");
      router.push("/pricing");
      return;
    }
    if (!tx_ref || !status || !transaction_id) return;

    const gen = CustomCookieUtil.getCookie("gen_pdf");

    const verifyPayment = async () => {
      try {
        const response = await fetch("/api/v1/payments/verify", {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            payment_reference: tx_ref || transaction_id,
            tx_reference: transaction_id || tx_ref,
            provider: "flutterwave",
            ...(gen && { gen_pdf: gen === "true" }),
          }),
        });

        if (response.status === 401) {
          setResStatus("signin_required");
          router.replace(
            `/signin?next=${encodeURI(
              `/checkout/purchase?tx_ref=${tx_ref}&transaction_id=${transaction_id}`,
            )}`,
          );
          return;
        }

        if (!response.ok) {
          // if (response.status === 429) {
          // 	setTimeout(() => {}, 5000);
          // }
          setResStatus("server_error");
          setMessage("Payment verification failed. PAY#004");
          return;
        }

        const data: ApiVerifyPayResponseI = await response.json();
        const dataStatus = data?.data?.status ?? "failed";

        if (
          ["success", "paid", "approved", "successful"].includes(dataStatus)
        ) {
          setResStatus("successful");
          try {
            const GA_ID = process.env.NEXT_PUBLIC_GA_ID;
            const GA_PATH = process.env.NEXT_PUBLIC_GA_PATH;
            const amount = data?.data?.amount;
            if (
              typeof window !== "undefined" &&
              window.gtag &&
              !data.message.startsWith(
                "Payment already verified as successful!",
              ) &&
              GA_ID &&
              GA_PATH &&
              amount
            ) {
              window.gtag("event", "conversion", {
                send_to: `${GA_ID}/${GA_PATH}`,
                value: /^\d$/.test(amount) ? parseInt(amount, 10) : 1,
                currency: "USD",
                transaction_id: data.data.tx_reference,
              });
              console.log("[Analytics] Conversion event sent to Google Ads");
            } else {
              if (!window.gtag)
                console.warn("[Analytics] gtag not found on window");
              if (!GA_ID || !GA_PATH)
                console.warn("[Analytics] GA environment variables missing");
            }
          } catch (error) {
            console.error(
              "Failed to track conversion:",
              (error as Error).message,
            );
          }

          if ((gen && gen === "true") || data.gen_pdf) {
            const ideaReply = localStorage.getItem("ideaReply");
            const parsedIdeaReply = ideaReply ? JSON.parse(ideaReply) : null;
            if (parsedIdeaReply && parsedIdeaReply.id) {
              const ideaId = parsedIdeaReply.id;

              const res = await fetch(`/api/v1/startup-ideas/${ideaId}`, {
                method: "GET",
                credentials: "include",
              });
              if (res.ok) {
                const ideaReply = (await res.json()).data;
                localStorage.setItem(
                  "ideaReply",
                  JSON.stringify({
                    preview: ideaReply.idea_validation,
                    ideaScore: ideaReply.idea_score,
                    prompt: ideaReply.prompt,
                    id: ideaReply.id,
                    sentReview: parsedIdeaReply.sentReview,
                    idx: parsedIdeaReply.idx,
                    canceledPay: true,
                  }),
                );
              }
            }
          }
          CustomCookieUtil.clearCookie("gen_pdf");
          router.replace(gen === "true" ? "/analysis" : "/");
          return;
        }

        if (status === "session_expired") {
          setResStatus("session_expired");
          setMessage("Payment canceled. Took Too Long");
          return;
        }

        if (dataStatus === "amount discrepancy") {
          setResStatus("amount_discrepancy");
          setMessage(
            "Payment amount mismatch. Please contact support at support@startinbox.tech",
          );
          return;
        }

        if (dataStatus === "not found") {
          setResStatus("not_found");
          scheduleRetry("not_found");

          return;
        }

        if (dataStatus === "pending") {
          setResStatus("pending");
          scheduleRetry("pending");
          return;
        }

        setResStatus("failed");
        setMessage("Payment failed. Please try again.");
      } catch (error) {
        console.error("Verification error:", error);
        setResStatus("server_error");
        setMessage("Unexpected verification error. PAY#005");
      }
    };

    verifyPayment();

    const scheduleRetry = (status: keyof typeof RETRY_CONFIG) => {
      const config = RETRY_CONFIG[status];

      if (!config) return;

      if (retryCount >= config.maxRetries || retryCount >= 3) {
        setResStatus("timeout");
        return;
      }

      animateProgress(config.progressStart, config.progressEnd, config.delayMs);

      retryTimerRef.current = setTimeout(() => {
        setRetryCount((r) => r + 1);
        verifyPayment(); // retry
      }, config.delayMs);
      console.log("retryCount: ", retryCount);
    };
  }, [tx_ref, transaction_id, retryCount, router, status]);
  useEffect(() => {
    return () => {
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current);
      }
    };
  }, []);

  const ui = UI_MAP[resStatus];

  const retryConfig = RETRY_CONFIG[resStatus as keyof typeof RETRY_CONFIG];

  const maxRetries =
    retryConfig && "maxRetries" in retryConfig ? retryConfig.maxRetries : 0;

  return (
    <StatusProgress
      label={ui.label}
      subLabel={
        retryCount > 0 &&
        ["not_found", "pending", "timeout"].includes(resStatus)
          ? `${message || ui.subLabel} (retry ${retryCount}/${maxRetries})`
          : message || ui.subLabel
      }
      intent={ui.intent}
      progress={retryCount > 0 ? progress : ui.progress}
    />
  );
};

export default PurchaseComponent;
