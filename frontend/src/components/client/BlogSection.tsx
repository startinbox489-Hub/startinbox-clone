"use client";

import { PostI } from "@/types/blogs.types";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

const BlogSection: React.FC<PostI> = (post) => {
  const [showMore, setShowMore] = useState(false);

  return (
    <section className="w-full py-20 bg-white">
      <div className="max-w-6xl mx-auto px-6">
        {/* Heading */}
        <div className="text-center mb-14">
          <h2 className="text-4xl font-bold text-gray-900">Our Blog</h2>
          <p className="text-gray-600 mt-3">
            Tips, stories, and guides to help you turn ideas into thriving
            startups.
          </p>
        </div>

        {/* Blog Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
          {/* Left */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              {post.title}
            </h3>

            <p className="text-gray-700 leading-relaxed">
              {showMore ? post.longExcerpt || "" : post.shortExcerpt || ""}
              {!showMore && (
                <button
                  onClick={() => setShowMore(true)}
                  className="text-blue-600 ml-1 hover:underline"
                >
                  Read more
                </button>
              )}
            </p>

            <p className="mt-4 text-gray-500 text-sm">{post.date}</p>

            <Link
              href={`/blogs/${post.id}`}
              className="text-blue-700 font-semibold mt-6 inline-block hover:underline"
            >
              Full Blog
            </Link>
          </div>

          {/* Right (Image) */}
          <div>
            <Image
              src={post.image}
              alt={post.title}
              width={180}
              height={90}
              className="rounded-xl shadow-lg w-full object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default BlogSection;
