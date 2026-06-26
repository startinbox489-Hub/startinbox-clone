"use client";

import { useState } from "react";
import OneOffSubscription from "./OneOffSubscription/OneOffSubscription";
import { IPricingProps } from "./interface";
import CreditSubscription from "./CreditSubscription/CreditSubscription";
import { TPricingType } from "@/types/pricingPlan.type";

const Pricing = ({ heading, subheading, plans }: IPricingProps) => {
  const [pricingStage, setPricingStage] = useState<"oneoff" | "credit">(
    "oneoff",
  );

  const oneoff = plans.filter((p) => p.type === TPricingType.ONEOFF);
  const reoccurring = plans.filter((p) => p.type === TPricingType.REOCCURRING);

  const stage =
    pricingStage === "oneoff" ? (
      <OneOffSubscription
        heading={heading}
        plans={oneoff}
        subheading={subheading}
      />
    ) : (
      <CreditSubscription plans={reoccurring} />
    );

  return (
    <div>
      <div className="flex flex-col items-center justify-center bg-gray-50 min-h-screen">
        <div className="relative">
          <div
            className={`absolute -top-12 ${pricingStage === "oneoff" ? "right-0" : "right-50"} transition-opacity duration-300 ${
              pricingStage === "oneoff" ? "opacity-100" : "opacity-80"
            }`}
          >
            <div className="relative bg-black text-white text-sm font-medium py-2 px-4 rounded-lg shadow-lg">
              See more
              <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-black rotate-45"></div>
            </div>
          </div>

          {/* Toggle Container */}
          <div
            className="relative flex items-center w-80 h-16 p-1 bg-white border border-gray-200 rounded-full shadow-sm cursor-pointer"
            onClick={() =>
              setPricingStage(pricingStage === "oneoff" ? "credit" : "oneoff")
            }
          >
            {/* Sliding Background */}
            <div
              className={`absolute h-[85%] w-[48%] bg-blue-600 rounded-full transition-all duration-300 ease-in-out shadow-md ${
                pricingStage === "credit"
                  ? "translate-x-[104%]"
                  : "translate-x-1"
              }`}
            />

            <button
              className={`relative z-10 flex-1 text-center text-lg font-semibold transition-colors duration-200 ${
                pricingStage === "oneoff" ? "text-white" : "text-gray-400"
              }`}
            >
              One Off
            </button>

            <button
              className={`relative z-10 flex-1 text-center text-lg font-semibold transition-colors duration-200 ${
                pricingStage === "credit" ? "text-white" : "text-gray-400"
              }`}
            >
              Subscription
            </button>
          </div>
        </div>
        {stage}
      </div>
    </div>
  );
};

export default Pricing;
