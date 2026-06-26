"use client";

import { ReviewData, ReviewPopupProps } from "@/types/reviewPopup.types";
import React, { useState, useCallback } from "react";

export default function ReviewPopup({
  idea_id,
  onClose,
  sendReviewToBackend,
  isOpen,
}: ReviewPopupProps) {
  const [review, setReview] = useState<ReviewData>({
    rating: null,
    feedback: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (review.rating === null) {
      setError("Please select a star rating.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Send the combined data
      await sendReviewToBackend({ ...review, idea_id });
      // On success, close the modal and inform the parent that a review was submitted
      onClose(true);
    } catch (err) {
      console.error("Review submission failed:", err);
      setError("Submission failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSkip = useCallback(() => {
    // The user clicks the X button to skip, inform the parent that no review was submitted
    onClose(false);
  }, [onClose]);

  if (!isOpen) {
    return null;
  }

  // --- Star Rating Component ---
  const StarRating = () => (
    <div className="flex justify-center space-x-2 my-4">
      {[1, 2, 3, 4, 5].map((starValue) => (
        <svg
          key={starValue}
          onClick={() => {
            setReview((prev) => ({ ...prev, rating: starValue }));
            setError(null);
          }}
          className={`w-10 h-10 cursor-pointer transition duration-150 ease-in-out ${
            starValue <= (review.rating || 0)
              ? "text-yellow-400 fill-yellow-400"
              : "text-gray-300 fill-transparent hover:text-yellow-300 hover:fill-yellow-300"
          }`}
          viewBox="0 0 24 24"
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
          stroke="currentColor"
          strokeWidth="1.5"
        >
          <path d="M12 2.5l2.67 7.73H22l-6.5 4.73 2.67 7.73L12 17.75l-6.84 4.94 2.67-7.73L2 10.23h7.33L12 2.5z" />
        </svg>
      ))}
    </div>
  );

  return (
    // Modal Overlay
    <div className="fixed inset-0 bg-gray-900 bg-opacity-70 flex items-center justify-center z-50 p-4">
      {/* Modal Content */}
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-sm transform transition-all duration-300 scale-100">
        {/* Close/Skip Button */}
        <button
          onClick={handleSkip}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 transition"
          aria-label="Skip review and close"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>

        <div className="p-8">
          <h2 className="text-2xl font-bold text-center text-gray-800 mb-2">
            Review
          </h2>
          <p className="text-sm text-center text-gray-500 mb-4">
            Please rate your experience on StartInBox
          </p>

          <StarRating />

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="feedback"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Additional feedback
              </label>
              <textarea
                id="feedback"
                value={review.feedback}
                onChange={(e) =>
                  setReview((prev) => ({ ...prev, feedback: e.target.value }))
                }
                rows={5}
                className="w-full border border-gray-300 rounded-lg p-3 shadow-sm resize-none focus:ring-purple-500 focus:border-purple-500 text-black"
                placeholder="Share your thoughts..."
              ></textarea>
            </div>

            {error && (
              <p className="text-sm text-red-500 text-center">{error}</p>
            )}

            <button
              type="submit"
              disabled={review.rating === null || isSubmitting}
              className={`w-full text-white font-semibold py-3 rounded-lg shadow-lg transition duration-300 ease-in-out ${
                review.rating === null || isSubmitting
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 transform hover:scale-[1.01]"
              }`}
            >
              {isSubmitting ? "Submitting..." : "Submit Review"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
