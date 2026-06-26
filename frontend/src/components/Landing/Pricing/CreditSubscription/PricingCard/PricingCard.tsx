"use client";

import { Check, ChevronRight } from "lucide-react";
import { IPricingCardProps } from "./interface";

const PricingCard = ({ plan, setSelectedPlan }: IPricingCardProps) => {
  return (
    <div
      className={`relative flex flex-col p-8 bg-white rounded-xl border-2 transition-all duration-200 ${
        plan.is_popular
          ? "border-indigo-500 shadow-xl scale-105 z-10"
          : "border-gray-100"
      }`}
      onClick={() => setSelectedPlan(plan)}
    >
      {plan.is_popular && (
        <span className="absolute top-2 right-1 px-3 py-1 text-xs font-semibold text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-full">
          Popular Plan
        </span>
      )}
      {plan.name.startsWith("Diamond") && (
        <span className="absolute top-2 right-1 px-3 py-1 text-xs font-semibold text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-full">
          Marketers Plan - {plan.credits} Credits
        </span>
      )}

      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          {plan.name} - {plan.credits} Credits
        </h3>
        <div className="mt-4 flex items-baseline">
          <span className="text-3xl font-extrabold tracking-tight text-gray-900">
            {`$${plan.price}`}
          </span>
          <span className="ml-1 text-xl font-medium text-gray-500">
            / {plan.period}
          </span>
        </div>
        <p className="mt-6 text-sm italic leading-relaxed text-gray-600">
          {plan.description}
        </p>
      </div>

      <ul className="space-y-4 mb-8 flex-1">
        {plan.features.map((feature, index) => (
          <li key={index} className="flex items-start">
            <Check className="h-5 w-5 text-green-500 shrink-0" />
            <span className="ml-3 text-sm text-gray-700">{feature.name}</span>
          </li>
        ))}
      </ul>

      <button
        className={`w-full py-4 px-6 rounded-lg font-semibold flex items-center justify-center transition-colors ${
          plan.is_popular
            ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:opacity-90"
            : "bg-white border border-gray-200 text-gray-900 hover:bg-gray-50"
        }`}
      >
        {plan.buttonText}
        <ChevronRight className="ml-2 h-4 w-4" />
      </button>
    </div>
  );
};

export default PricingCard;
