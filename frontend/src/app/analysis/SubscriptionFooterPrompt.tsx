"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import CustomCookieUtil from "@/lib/client/setCookie";

const sheetVariants = {
  hidden: { y: "100%" },
  visible: {
    y: 0,
    transition: { type: "spring" as const, stiffness: 260, damping: 28 },
  },
  exit: { y: "100%", transition: { duration: 0.25 } },
};

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 },
};

const SubscriptionFooterPrompt: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const setStatus = () => {
    const ideaReply = localStorage.getItem("ideaReply");
    const parsed = ideaReply ? JSON.parse(ideaReply) : null;
    if (parsed) {
      localStorage.setItem(
        "ideaReply",
        JSON.stringify({ ...parsed, canceledPay: true }),
      );
    }
  };

  const handleClose = () => {
    setStatus();
    setIsVisible(false);
  };

  const handlePay = () => {
    setStatus();
    CustomCookieUtil.setCookie("gen_pdf", "true", { mins: 30 });
    window.location.href = "/pricing";
  };

  const message =
    "Unlock **Full Validation**: Subscribe now to instantly access the Complete Idea Report and receive the full PDF & DOCX formats via email.";

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 z-40 bg-black/40 "
            variants={backdropVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            // onClick={handleClose}
          />

          {/* Bottom Sheet */}
          <motion.div
            className="
							fixed bottom-0 left-0 right-0 z-50
							mx-auto w-full max-w-3xl
							h-[50vh] max-h-[420px]
							bg-white rounded-t-3xl shadow-2xl
							flex flex-col
						"
            variants={sheetVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.2}
            // onDragEnd={(_, info) => {
            // 	if (info.offset.y > 120) handleClose();
            // }}
          >
            {/* Drag Handle */}
            <div className="w-12 h-1.5 bg-gray-300 rounded-full mx-auto mt-3 mb-4" />

            {/* Content */}
            <div className="flex-1 px-6 text-center flex flex-col justify-center">
              <h2 className="text-2xl font-extrabold text-gray-900 mb-3">
                Get Full Access
              </h2>

              <p
                className="text-gray-700 text-sm md:text-base leading-relaxed"
                dangerouslySetInnerHTML={{
                  __html: message.replace(/\*\*(.*?)\*\*/g, "<b>$1</b>"),
                }}
              />
            </div>

            {/* Actions */}
            <div className="px-6 pb-6 flex flex-col gap-3">
              <button
                onClick={handlePay}
                className="w-full py-3 rounded-lg text-white font-semibold bg-indigo-600 hover:bg-indigo-700 transition"
              >
                Subscribe Now
              </button>

              <button
                onClick={handleClose}
                className="w-full py-2 text-sm text-gray-500 hover:text-gray-700 transition"
              >
                Not now
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default SubscriptionFooterPrompt;
