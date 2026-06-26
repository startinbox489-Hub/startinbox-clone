import React from "react";
import Image from "next/image";
import { AllInOnePlatformSectionProps } from "./interface";

const AllInOnePlatformSection: React.FC<AllInOnePlatformSectionProps> = ({
  heading,
  subheading,
  featureCards,
}) => {
  return (
    <section
      id="features"
      className="py-16 px-4 sm:px-6 lg:px-8 bg-white pt-30 pb-19"
    >
      <div className="max-w-7xl mx-auto text-center mb-12">
        {/* Main Heading */}
        <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-3">
          {heading}
        </h2>
        {/* Subheading */}
        <p className="text-lg text-gray-600">{subheading}</p>
      </div>

      {/* Feature Cards Container */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {featureCards.map((card, index) => (
          <div
            key={index}
            className="bg-white rounded-xl shadow-lg p-8 flex flex-col items-start text-left border border-gray-100"
          >
            {/* Icon */}
            <div className="w-12 h-12 flex items-center justify-center rounded-full bg-blue-100 mb-6">
              <Image
                src={card.iconSrc}
                alt={card.altText}
                className="w-6 h-6 text-blue-600"
                width={150}
                height={50}
              />
              {/* <img src={card.iconSrc} alt={card.altText} className="w-6 h-6 text-blue-600" /> */}
            </div>

            {/* Title */}
            <h3 className="text-xl font-bold text-gray-900 mb-3">
              {card.title}
            </h3>

            {/* Description */}
            <p className="text-base text-gray-600 mb-6 min-h-[48px]">
              {" "}
              {/* Min-height for alignment */}
              {card.description}
            </p>

            {/* List of Items */}
            <ul className="space-y-2 text-gray-700">
              {card.items.map((item, itemIndex) => (
                <li key={itemIndex} className="flex items-center">
                  <span className="text-purple-600 text-lg mr-2">•</span>{" "}
                  {/* Custom bullet */}
                  <span>{item.text}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
};

export default AllInOnePlatformSection;
