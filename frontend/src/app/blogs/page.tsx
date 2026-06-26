import { Metadata } from "next";
import BlogList from "./components/BlogList";
import PostsService from "@/lib/server/getPosts";
import { Suspense } from "react";

const BASE_URL = process.env.NEXT_PUBLIC_NEXTAUTH_URL;
export const dynamic = "force-dynamic";

export async function generateMetadata({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}): Promise<Metadata> {
  const params = await searchParams;
  const page = Number(params?.page || 1);
  const titleSuffix = page > 1 ? ` - Page ${page}` : "";

  const baseTitle = "Startinbox Insight & Articles";
  const description =
    "Explore the latest insights and articles from Startin Box on emerging technologies, business trends, and innovation strategies.";

  const currentUrl = `${BASE_URL}/bogs?page=${page}`;
  const previousUrl = page > 1 ? `${BASE_URL}/blogs?page=${page - 1}` : null;
  const nextUrl = `${BASE_URL}/blogs?page=${page + 1}`;

  return {
    title: `${baseTitle}${titleSuffix}`,
    description,
    alternates: {
      canonical: currentUrl,
    },
    openGraph: {
      title: `${baseTitle}${titleSuffix}`,
      description,
      url: currentUrl,
      siteName: "Startin Box",
      images: [
        {
          url: `${BASE_URL}/images/unsplash_77JACslA8G0.png`,
          width: 1200,
          height: 630,
          alt: "Startinbox Blog",
        },
      ],
      locale: "en_US",
      type: "website",
    },
    other: {
      ...(previousUrl && { prev: previousUrl }),
      next: nextUrl,
    },
  };
}

export default async function BlogPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const params = await searchParams;
  const page = Number(params.page) || 1;
  const { data: posts, pages } = await PostsService.getPosts(page);

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <main className="bg-gray-50 min-h-screen py-10">
        <section className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-8">
            <p className="text-sm text-purple-600 font-semibold mb-2">
              Our Blog
            </p>
            <h1 className="text-3xl font-bold text-gray-900">
              Startinbox Insight & Articles
            </h1>
          </div>
          <BlogList posts={posts} currentPage={page} totalPages={pages} />
        </section>
      </main>
    </Suspense>
  );
}
