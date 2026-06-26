"use client";

import React, { useEffect } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { RegistrationSuccessPopupProps } from "@/types/signup.types";

const RegistrationSuccessPopup: React.FC<RegistrationSuccessPopupProps> = ({
  userName,
  onClose,
  autoCloseDelay = 5000, // Default to 5 seconds
  homepagePath = "/", // Default to root
  homePageName = "Home Page",
}) => {
  const router = useRouter();

  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;
    if (autoCloseDelay > 0) {
      timer = setTimeout(() => {
        onClose();
      }, autoCloseDelay);
    }

    return () => {
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [autoCloseDelay, onClose]);

  const handleGoToHomepage = () => {
    onClose(); // Close the popup
    router.push(homepagePath); // Navigate to the homepage
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="relative bg-white p-8 sm:p-12 rounded-lg shadow-xl text-center max-w-lg w-full">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 focus:outline-none"
          aria-label="Close"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Success Icon */}
        <div className="mb-6">
          <Image
            src="/startinbox-newsletter-popup-logo.png"
            alt="Success Checkmark"
            width={100}
            height={100}
            className="mx-auto"
          />
        </div>

        {/* Messages */}
        <h2 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2">
          Congratulations, {userName || ""}
        </h2>
        <p className="text-gray-600 text-lg mb-8">
          Registration successful, welcome to Startin Box
        </p>

        {/* Homepage Button */}
        <button
          onClick={handleGoToHomepage}
          className="w-full max-w-xs py-3 rounded-lg text-white font-semibold text-lg transition-transform transform hover:scale-105"
          style={{
            background: "linear-gradient(to right, #6D28D9, #A78BFA)",
          }}
        >
          {homePageName}
        </button>
      </div>
    </div>
  );
};

export default RegistrationSuccessPopup;
