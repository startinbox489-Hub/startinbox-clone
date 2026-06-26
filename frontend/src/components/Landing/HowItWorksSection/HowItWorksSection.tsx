import { HowItWorksSectionProps } from "./interface";
import React from "react";

const HowItWorksSection = ({
  heading,
  subheading,
  steps,
  ctaButtonText,
  ctaButtonLink,
  ctaSubtext,
}: HowItWorksSectionProps) => {
  return (
    <section
      id="how-it-works"
      className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-100 pt-30 pb-26"
    >
      <div className="max-w-6xl mx-auto text-center">
        {/* Main Heading */}
        <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-3">
          {heading}
        </h2>
        {/* Subheading */}
        <p className="text-lg text-gray-600 mb-12">{subheading}</p>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 lg:gap-16 mb-16">
          {steps.map((step) => (
            <div key={step.number} className="flex flex-col items-center">
              <div className="relative mb-6">
                {/* Step Number Circle */}
                <div className="w-12 h-12 flex items-center justify-center rounded-full bg-black text-white text-xl font-bold">
                  {step.number}
                </div>
              </div>
              {/* Step Title */}
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {step.title}
              </h3>
              {/* Step Description */}
              <p className="text-base text-purple-600 px-4">
                {step.description}
              </p>
            </div>
          ))}
        </div>

        {/* Call to Action */}
        <div className="mt-12">
          <p className="text-gray-700 text-lg font-medium mb-4">{ctaSubtext}</p>
          <a
            href={ctaButtonLink}
            className="inline-block py-3 px-8 rounded-lg text-white font-semibold text-lg transition-transform transform hover:scale-105"
            style={{
              background: "linear-gradient(to right, #6D28D9, #A78BFA)",
            }}
          >
            {ctaButtonText}
          </a>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
