"use client";

import React, { useState, useCallback, useMemo, useEffect } from "react";
import { Loader2, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { track } from "@/lib/client/metaPixel";
import {
  IdeaModelI,
  TempIdeaI,
} from "../Landing/ValidateIdeaSection/interface";

const WARNINGTHRESHOLD = 80;

const BusinessIdeaValidator: React.FC = () => {
  const router = useRouter();

  const [ideaInput, setIdeaInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [tempIdea, setTempIdea] = useState<TempIdeaI | null>(null);
  const [showCharCount, setShowCharCount] = useState<boolean>(false);

  const closeModal = useCallback(() => setError(null), []);

  const percentage = useMemo(() => {
    return Math.round((ideaInput.length / 4_000) * 100);
  }, [ideaInput.length]);

  const isNearLimit = useMemo(() => {
    return percentage >= WARNINGTHRESHOLD;
  }, [percentage]);

  const isOverLimit = useMemo(() => {
    return ideaInput.length > 4_000;
  }, [ideaInput.length]);

  useEffect(() => {
    const tempIdeaExists = localStorage.getItem("tempIdea");
    if (tempIdeaExists) {
      setTempIdea(JSON.parse(tempIdeaExists));
      setIdeaInput(tempIdea?.tempIdea || "");
    }
  }, [tempIdea?.tempIdea]);

  const validateIdea = useCallback(async () => {
    const idea = ideaInput.trim();

    if (idea.length < 20) {
      setError(
        "Please enter a more detailed business idea (at least 20 characters) for a meaningful validation.",
      );
      return;
    }

    // Reset state and show loading
    setError(null);
    setIsLoading(true);
    // for META PIXEL
    const event_id = track("Lead", { category: "idea_validation" });

    try {
      const res = await fetch("/api/v1/validateidea", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt: idea }),
        credentials: "include",
      });
      if (!res.ok) {
        if (res.status === 401) {
          if (ideaInput) {
            localStorage.setItem(
              "tempIdea",
              JSON.stringify({ ...tempIdea, tempIdea: ideaInput }),
            );
          }
          throw new Error("Sign in required");
        } else if ([409, 417].includes(res.status)) {
          const data = await res.json();
          throw new Error(data?.message);
        } else if (res.status === 429) {
          return;
        } else if (res.status === 422) {
          const data = await res.json();
          throw new Error(data.message);
        }
        const errorBody = await res.json();
        throw new Error(`${errorBody.message || res.statusText}`);
      }
      const data = await res.json();
      // console.log('data: ', data);
      const ideaReply: IdeaModelI = data?.idea;
      localStorage.setItem(
        "ideaReply",
        JSON.stringify({
          preview: ideaReply.idea_validation,
          ideaScore: ideaReply.idea_score,
          prompt: idea,
          id: ideaReply.id,
          sentReview: false,
          idx: data.idx,
          canceledPay: false,
        }),
      );
      // redirect to analysis
      router.push("/analysis");
      return;
    } catch (err) {
      const errorMessage =
        (err as Error).message ||
        "An unknown error occurred during validation.";

      if (errorMessage.startsWith("Sign in required")) {
        router.push("/signin");
        return;
      }
      setError(`Validation failed: ${errorMessage}`);
    } finally {
      // Hide loading
      setIsLoading(false);
    }
  }, [ideaInput, router, tempIdea]);

  // ++++++++++++++++++ HANDLE IDEA CHANGE ++++++++++++++++++++++++
  const handleIdeaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setIdeaInput(newValue);
    if (newValue.trim() !== "") {
      setShowCharCount(true);
    } else {
      setShowCharCount(false);
    }

    if (newValue === "") {
      setError("");
      return;
    } else {
      setError("");
    }
  };

  return (
    <div className="flex justify-center items-center pt-20">
      <div className="w-full max-w-4xl flex flex-col items-center space-y-10">
        {/* Custom CSS for gradients */}
        <style>{`
                .gradient-text {
                    background-image: linear-gradient(to right, #8a2be2, #4169e1, #00ced1, #ff69b4);
                    -webkit-background-clip: text;
                    background-clip: text;
                    color: transparent;
                    font-weight: 800;
                }
                .gradient-button {
                    background: linear-gradient(135deg, #8a2be2 0%, #a020f0 100%);
                    transition: all 0.2s ease-in-out;
                }
                .gradient-button:hover {
                    box-shadow: 0 8px 20px rgba(160, 32, 240, 0.4);
                    transform: translateY(-2px);
                }
            `}</style>

        {/* Title */}
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight text-center">
          What is your <span className="gradient-text">business idea</span>?
        </h1>

        {/* Input Card */}
        <div className="w-full bg-white p-6 sm:p-10 rounded-2xl shadow-2xl transition duration-300 transform hover:shadow-3xl">
          <textarea
            id="ideaInput"
            rows={8}
            value={ideaInput}
            onChange={handleIdeaChange}
            placeholder="I want to build a SaaS that..."
            className={`w-full text-lg p-4 resize-none border-2  rounded-xl focus:ring-purple-500  transition duration-150 outline-none placeholder-gray-400 text-black ${
              isOverLimit
                ? "focus:border-red-500 border-red-600"
                : isNearLimit
                  ? "focus:border-yellow-500 border-yellow-600"
                  : "focus:border-purple-500 border-purple-600"
            }`}
            disabled={isLoading}
            maxLength={4_002}
            required
          ></textarea>
          {showCharCount && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-0">
              {/* Character Count */}
              <div className="text-sm">
                <span
                  className={
                    isOverLimit ? "text-red-600 font-medium" : "text-green-600"
                  }
                >
                  {ideaInput.length} / {4_000} characters
                </span>
                {isOverLimit ? (
                  <span className="ml-2 text-red-600">
                    ({ideaInput.length - 4_000} over limit)
                  </span>
                ) : (
                  ideaInput !== "" &&
                  ideaInput.length < 20 && (
                    <span className="ml-2 text-red-600">Too short</span>
                  )
                )}
              </div>

              {/* Progress bar */}
              <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full ${
                    isOverLimit
                      ? "bg-red-500"
                      : isNearLimit
                        ? "bg-yellow-500"
                        : "bg-green-500"
                  }`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>
            </div>
          )}

          <div className="flex justify-center mt-6">
            <button
              onClick={validateIdea}
              className="gradient-button text-white text-xl font-semibold py-3 px-12 rounded-full shadow-lg transition duration-200 disabled:opacity-50 disabled:shadow-none flex items-center justify-center"
              disabled={isLoading || ideaInput.trim().length < 20}
            >
              {isLoading ? (
                <Loader2 className="animate-spin h-6 w-6 mr-2" />
              ) : (
                "Validate Now"
              )}
            </button>
          </div>
        </div>

        {/* Custom Modal for Errors */}
        {error && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-2xl w-full max-w-sm text-center">
              <div className="flex justify-end">
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-700"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
              <h3 className="text-xl font-bold text-red-600 mb-4 mt-2">
                Error
              </h3>
              <p className="text-gray-700 mb-6">{error}</p>
              <button
                onClick={closeModal}
                className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BusinessIdeaValidator;
