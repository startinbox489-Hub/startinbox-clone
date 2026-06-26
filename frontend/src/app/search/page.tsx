import { SearchPageProps } from "@/types/search.types";
import { redirect } from "next/navigation";
export const dynamic = "force-dynamic";

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const { q } = await searchParams;

  switch (q.trim().toLowerCase()) {
    case "home":
      redirect("/");
    case "blog":
      redirect("/blogs");
    case "blogs":
      redirect("/blogs");
    case "faq":
      redirect("/#faq");
    case "faqs":
      redirect("/#faq");
    case "price":
      redirect("/#pricing");
    case "pricing":
      redirect("/#pricing");

    default:
      redirect("/");
  }
}
