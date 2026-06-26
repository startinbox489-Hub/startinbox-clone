"use client";

import { useState, useRef, useEffect } from "react";
import { motion, useMotionValue } from "framer-motion";
import TestimonialCard from "./TestimonialCard";
import { TestimonialsI } from "./interface";

const Testimonial = () => {
  const [testimonials, setTestimonials] = useState<TestimonialsI[]>([]);
  const [index, setIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const x = useMotionValue(0);
  const [isPaused, setIsPaused] = useState(false);
  const autoplayIntervalRef = useRef<ReturnType<typeof setInterval> | null>(
    null,
  );
  const [cardsToShow, setCardsToShow] = useState(1); // Default to 1 for small screens

  const fetchTestimonials = async () => {
    try {
      const response = await fetch("/api/v1/testimonials", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        next: { revalidate: 3600 }, // every 1 hour
      });

      if (response.ok) {
        const fetchedTestimonials = (await response.json()).data;
        if (fetchedTestimonials.length > 0) {
          setTestimonials(fetchedTestimonials);
        }
        return fetchedTestimonials;
      } else {
      }
    } catch (error) {
      setTestimonials([]);
      return [];
    }
  };

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        // Large screens (lg)
        setCardsToShow(4);
      } else if (window.innerWidth >= 768) {
        // Medium screens (md)
        setCardsToShow(2);
      } else {
        // Small screens
        setCardsToShow(1);
      }
    };

    fetchTestimonials();

    // Set initial value and add event listener
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const getCardOffset = () => {
    if (containerRef.current) {
      const card =
        containerRef.current.querySelector<HTMLDivElement>(".flex-shrink-0");
      if (!card) return 0;
      const cardWidth = card.offsetWidth;
      const cardMargin = 16; // Tailwind's mx-4 is 1rem = 16px
      const totalCardWidth = cardWidth + cardMargin * 2;
      return -(index * totalCardWidth);
    }
    return 0;
  };

  useEffect(() => {
    if (isPaused) {
      if (autoplayIntervalRef.current) {
        clearInterval(autoplayIntervalRef.current);
      }
    } else {
      autoplayIntervalRef.current = setInterval(() => {
        setIndex((prevIndex) => {
          const nextIndex = prevIndex + cardsToShow;
          // Loop back to the beginning if we've reached the end
          if (nextIndex >= testimonials.length) {
            return 0;
          }
          return nextIndex;
        });
      }, 5000); // Change slide every 5 seconds
    }

    return () => {
      if (autoplayIntervalRef.current) {
        clearInterval(autoplayIntervalRef.current);
      }
    };
  }, [isPaused, cardsToShow, testimonials]);

  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4 text-center">
        <h2 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4">
          TESTIMONIALS
        </h2>
        <p className="text-xl text-gray-500 mb-12">
          What people that have used Startinbox say about us.
        </p>
        <div className="relative overflow-hidden w-full">
          <motion.div
            ref={containerRef}
            className="flex w-full cursor-grab"
            style={{ x }}
            drag="x"
            dragConstraints={{ left: -1000, right: 0 }}
            dragElastic={0.1} // new
            onDragStart={() => setIsPaused(true)}
            onDragEnd={(_, info) => {
              if (info.offset.x < -50) {
                setIndex((prev) =>
                  Math.min(
                    prev + cardsToShow,
                    testimonials.length - cardsToShow,
                  ),
                );
              } else if (info.offset.x > 50) {
                setIndex((prev) => Math.max(prev - cardsToShow, 0));
              }
              setIsPaused(false);
            }}
            animate={{ x: getCardOffset() }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            {testimonials.map((testimonial, idx) => (
              <TestimonialCard
                key={idx}
                testimonial={testimonial.testimonial}
                firstname={testimonial.firstname}
                lastname={testimonial.lastname}
                rating={testimonial.rating}
                image_url={testimonial.image_url}
              />
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Testimonial;
