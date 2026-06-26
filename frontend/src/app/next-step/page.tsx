"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import ProjectDetailsForm from "./components/ProjectDetailsForm";
export const dynamic = "force-dynamic";

export default function DetailsPage() {
  const router = useRouter();
  const [ideaReplyId, setIdeaReplyId] = useState<string | null>(null);
  // console.log('ideaReplyId: ', ideaReplyId);

  const handleNavigation = () => {
    router.push("/#validate-idea-sec");
  };

  useEffect(() => {
    const ideaReplyExists = localStorage.getItem("ideaReply");
    if (ideaReplyExists) {
      setIdeaReplyId((prev) => (prev = JSON.parse(ideaReplyExists).id));
    }
  }, []);
  if (!ideaReplyId) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <p className="text-gray-900">NOTHING TO SHOW HERE. </p>
        <br />
        <button className="text-green-600 border" onClick={handleNavigation}>
          VALIDATE NEW IDEA
        </button>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <h1 className="text-gray-900 text-2xl font-bold mb-6">
        Plan the Next Steps with Product Manager
      </h1>
      {ideaReplyId ? <ProjectDetailsForm ideaId={ideaReplyId} /> : ""}
    </div>
  );
}
