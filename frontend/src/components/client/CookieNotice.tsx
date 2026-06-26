"use client";

import React, { useState } from "react";
import { ArrowLeft, Cookie } from "lucide-react";

import { useCookieConsent } from "../../hooks/useCookieConsent";
import PrivacyPolicyContent from "../server/PrivacyPolicyContent";

const CookieNotice: React.FC = () => {
  const { giveConsent, isBannerVisible } = useCookieConsent();
  const [showFullPolicy, setShowFullPolicy] = useState(false); // state to switch views

  if (!isBannerVisible) {
    return null;
  }

  // Define the content based on state
  const ModalContent = showFullPolicy ? (
    <PrivacyPolicyContent />
  ) : (
    // Standard Cookie Notice Content
    <div className="space-y-6">
      {/* Header Icon and Title */}
      <div className="text-center">
        <Cookie className="w-10 h-10 text-indigo-600 dark:text-indigo-400 mx-auto mb-3" />
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Your Privacy Matters
        </h2>
      </div>

      {/* Display Text Area */}
      <div className="space-y-4 text-center text-base leading-relaxed">
        <p>
          <strong>🍪 We use cookies!</strong>
        </p>
        <p className="text-gray-600 dark:text-gray-300">
          Startinbox uses cookies to improve your browsing experience, analyze
          site traffic, and personalize our services. This helps us ensure the
          platform works effectively for validating your ideas.
        </p>
        <p className="font-medium">
          Please make a choice below. You can view the full policy before
          accepting.
        </p>
      </div>
    </div>
  );

  // Define the buttons based on state
  const ModalButtons = showFullPolicy ? (
    <div className="flex flex-col space-y-3">
      {/* Back Button */}
      <button
        onClick={() => setShowFullPolicy(false)}
        className="w-full px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-base font-semibold rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition duration-200"
      >
        <ArrowLeft className="w-4 h-4 inline mr-2" /> Back to Consent
      </button>
      {/* Accept Button */}
      <button
        onClick={giveConsent}
        className="w-full px-6 py-3 bg-indigo-600 text-white text-lg font-bold rounded-lg hover:bg-indigo-700 transition duration-200 shadow-lg"
      >
        Accept and Continue
      </button>
    </div>
  ) : (
    <div className="flex flex-col space-y-3">
      {/* Accept Cookies (Primary Action) */}
      <button
        onClick={giveConsent}
        className="w-full px-6 py-3 bg-indigo-600 text-white text-lg font-bold rounded-lg hover:bg-indigo-700 transition duration-200 shadow-lg"
      >
        Accept Cookies
      </button>

      {/* Learn More (Secondary Link) */}
      <button
        onClick={() => setShowFullPolicy(true)}
        className="w-full text-center px-6 py-3 text-indigo-600 dark:text-indigo-400 text-base font-medium rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition duration-200 border border-indigo-200 dark:border-indigo-700"
      >
        Learn More
      </button>
    </div>
  );

  return (
    <div className="fixed inset-0 z-[100] bg-black/70 flex items-center justify-center p-4 sm:p-8 backdrop-blur-sm">
      {/* CONTENT BOX */}
      <div
        className={`max-w-xl w-full bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 
                    rounded-xl shadow-2xl p-6 sm:p-8 space-y-6 transform transition-all duration-300 scale-100 
                    ${showFullPolicy ? "max-h-[90vh]" : "max-h-auto"}`} // Allow taller box for policy
      >
        {ModalContent}
        {ModalButtons}
      </div>
    </div>
  );
};

export default CookieNotice;
