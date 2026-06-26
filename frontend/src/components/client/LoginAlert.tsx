"use client";

import React, { useState } from "react";
import { Check } from "lucide-react";
import { LoginAlertCardProps } from "@/types/signup.types";
import { useRouter } from "next/navigation";

const LoginAlertCard = ({
  title = "Login Alert",
  message = "You need a StartinBox account to make payment and proceed to validate your ideas",
  signUpUrl = "/signup",
  signInUrl = "/signin",
  onClose,
}: LoginAlertCardProps) => {
  const router = useRouter();

  const [isSignin, setIsSignin] = useState<string | null>(null);
  const [isSignup, setIsSignup] = useState<string | null>(null);
  const [isRedirecting, setIsRedirecting] = useState(false);

  const handleSignin = () => {
    if (isRedirecting) return;
    setIsRedirecting(true);
    setIsSignin("Redirecting to Signin...");
    router.push(signInUrl);
    return;
  };

  const handleSignup = () => {
    if (isRedirecting) return;
    setIsRedirecting(true);
    setIsSignup("Redirecting to Signup...");
    router.push(signUpUrl);
    return;
  };
  const handleOnClose = () => {
    if (isRedirecting) return;
    setIsRedirecting(true);
    onClose();
    return;
  };
  return (
    <div className="flex items-center justify-center h-full w-full p-4">
      {/* Alert Card Container */}
      <div
        className={`
          w-full max-w-sm 
          bg-white rounded-xl shadow-2xl 
          p-8 text-center
          transform transition-all duration-300
        `}
      >
        <button
          className="text-black mb-4 font-medium hover:underline"
          onClick={handleOnClose}
          aria-disabled={isRedirecting}
          aria-busy={isRedirecting}
          disabled={isRedirecting}
        >
          Back
        </button>

        {/* Checkmark Icon Container */}
        <div className="flex justify-center mb-6">
          <div className="bg-blue-600 rounded-full p-3 shadow-lg shadow-blue-500/50">
            {/* Checkmark Icon */}
            <Check className="w-12 h-12 text-white font-bold" strokeWidth={4} />
          </div>
        </div>
        {/* Main Title */}
        <h1 className="text-2xl font-extrabold text-gray-900 mb-4 tracking-tight">
          {title}
        </h1>
        {/* Explanatory Message */}
        <p className="text-base text-gray-600 mb-8 max-w-xs mx-auto">
          {message}
        </p>
        {/* Action Buttons Container */}
        <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4 justify-center">
          {/* Secondary Button: Sign Up */}
          <button
            type="button"
            onClick={handleSignup}
            aria-disabled={isRedirecting}
            aria-busy={isRedirecting}
            disabled={isRedirecting}
            className={`
                            inline-flex items-center justify-center
                            w-full sm:w-1/2 py-3 px-6 rounded-lg 
                            font-semibold text-gray-800 text-base
                            border border-gray-300 bg-white
                            disabled:opacity-60 disabled:cursor-not-allowed
                            hover:bg-gray-100 hover:border-gray-400
                            transition
                        `}
          >
            {isSignup ?? "Sign Up"}
          </button>

          {/* Primary Button: Sign In */}
          <button
            type="button"
            onClick={handleSignin}
            aria-disabled={isRedirecting}
            aria-busy={isRedirecting}
            disabled={isRedirecting}
            className={`
                            inline-flex items-center justify-center
                            w-full sm:w-1/2 py-3 px-6 rounded-lg 
                            font-semibold text-white text-base
                            bg-gradient-to-r from-blue-600 to-purple-700
                            shadow-md transition
                            hover:shadow-lg hover:opacity-95
                            disabled:opacity-60 disabled:cursor-not-allowed
                        `}
          >
            {isSignin ?? "Sign In"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginAlertCard;
