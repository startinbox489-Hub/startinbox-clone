"use client";

import { useEffect, useState } from "react";
import PricingCard from "./PricingCard/PricingCard";
import { ICreditsubscriptionProps } from "./interface";
import { TSelectedPlan } from "./PricingCard/interface";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthProvider";
import toast from "react-hot-toast";
import { Check } from "lucide-react";

const CreditSubscription = ({ plans }: ICreditsubscriptionProps) => {
  const router = useRouter();
  const { user } = useAuth();
  const [showPaymentModal, setShowPaymentModal] = useState<boolean>(false);
  const [paymentLink, setPaymentLink] = useState<string>("");
  const [selectedPlan, setSelectedPlan] = useState<TSelectedPlan | null>(null);

  useEffect(() => {
    if (selectedPlan) {
      const handleSelectPlan = async () => {
        if (!user) {
          toast.error("Please sign in first.");
          router.push(`/signin`);
          return;
        }
        try {
          const response = await fetch("/api/v1/billing", {
            method: "POST",
            body: JSON.stringify({ id: selectedPlan.flutterwave_plan_id }),
            credentials: "include",
          });

          const data = await response.json();
          if (!response.ok) {
            if (response.status === 401) {
              router.push(`/signin`);
            }
            if (response.status === 404) {
              toast.error("Selected Plan not found");
              return;
            }
            return;
          }
          setPaymentLink(data?.data?.link);
          const newWindow = window.open(data?.data?.link, "_blank");
          if (!newWindow || newWindow.closed) {
            setShowPaymentModal(true);
            return;
          }
        } catch (error) {
          console.error("Payment link generation failed:", error);
        }
      };
      handleSelectPlan();
    }
  }, [router, selectedPlan, user]);

  return (
    <section className="py-20 px-4 bg-gray-50 min-h-screen m-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-4xl font-black text-gray-900 uppercase tracking-tight mb-4">
            Simple And Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600">
            Choose a plan that matches your launch stage — no hidden fees,
            cancel anytime.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
          {plans.map((p) => {
            const plan = {
              ...p,
              period: p.id === "silver" ? "week" : "month",
              buttonText:
                p.id === "silver"
                  ? "Start Weekly Plan"
                  : p.id === "gold"
                    ? "Start Monthly Plan"
                    : "Start Marketers' Plan",
            };
            return (
              <PricingCard
                key={p.name}
                plan={plan}
                setSelectedPlan={(plan) => setSelectedPlan(plan)}
              />
            );
          })}
        </div>
      </div>
      {showPaymentModal && (
        <>
          <div
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 transition-opacity"
            onClick={() => setShowPaymentModal(false)}
          />

          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
              className={`
          w-full max-w-sm 
          bg-white rounded-xl shadow-2xl 
          p-8 text-center
          transform transition-all duration-300
          scale-100 opacity-100
          relative
        `}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Back button */}
              <button
                className="absolute top-4 left-4 text-gray-600 hover:text-gray-900 font-medium hover:underline flex items-center gap-1"
                onClick={() => setShowPaymentModal(false)}
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                Back
              </button>

              <div className="flex justify-center mb-6 mt-4">
                <div className="bg-blue-600 rounded-full p-3 shadow-lg shadow-blue-500/50">
                  <Check
                    className="w-12 h-12 text-white font-bold"
                    strokeWidth={4}
                  />
                </div>
              </div>

              <h1 className="text-2xl font-extrabold text-gray-900 mb-4 tracking-tight">
                {selectedPlan?.name}
              </h1>

              <p className="text-base text-gray-600 mb-8 max-w-xs mx-auto">
                Proceed to {selectedPlan?.name} subscription
              </p>

              <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4 justify-center">
                <a
                  href={paymentLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`
              inline-flex items-center justify-center
              w-full sm:w-1/2 py-3 px-6 rounded-lg 
              font-semibold text-white text-base
              bg-gradient-to-r from-blue-600 to-purple-700
              shadow-md transition-all duration-200
              hover:shadow-lg hover:opacity-95 hover:scale-105
              active:scale-100
              disabled:opacity-60 disabled:cursor-not-allowed
            `}
                >
                  Proceed
                </a>
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
};

export default CreditSubscription;
