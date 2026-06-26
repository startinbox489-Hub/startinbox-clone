"use client";

import Image from "next/image";
import React from "react";
import { TestimonialsI } from "./interface";

const TestimonialCard = ({
  testimonial,
  image_url,
  lastname,
  firstname,
  rating,
  // id,
}: TestimonialsI) => (
  <div className="flex-shrink-0 w-80 max-w-sm mx-4 bg-white p-8 rounded-lg shadow-lg border-2 border-purple-100 flex flex-col justify-between h-full">
    <div>
      <div className="text-4xl text-purple-500 mb-4 font-serif">“</div>
      <p className="text-gray-600 text-lg mb-6 leading-relaxed">
        {testimonial}
      </p>
    </div>
    <div className="flex items-center mt-auto">
      <Image
        src={image_url}
        alt={`${firstname} ${lastname}`}
        width={48}
        height={48}
        className="rounded-full ring-2 ring-purple-300"
      />
      <div className="ml-4">
        <h3 className="text-lg font-semibold text-gray-800">
          {`${firstname} ${lastname}`}
        </h3>
        <div className="flex text-yellow-400">
          {Array.from({ length: 5 }, (_, i) => (
            <svg
              key={i}
              className={`w-5 h-5 ${
                i < rating ? "text-yellow-400" : "text-gray-300"
              }`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.953a1 1 0 00.95.69l4.16.03c.962.006 1.343 1.258.583 1.831l-3.376 2.455a1 1 0 00-.364 1.118l1.286 3.953c.3.921-.755 1.688-1.516 1.125l-3.376-2.455a1 1 0 00-1.176 0l-3.376 2.455c-.761.563-1.817-.184-1.516-1.125l1.286-3.953a1 1 0 00-.364-1.118L.24 9.431c-.76-.573-.38-1.825.582-1.831l4.16-.03a1 1 0 00.95-.69l1.286-3.953z" />
            </svg>
          ))}
        </div>
      </div>
    </div>
  </div>
);

export default TestimonialCard;
