import { Suspense } from "react";
import AboutPageComponent from "./AboutPageComponent";
export const dynamic = "force-dynamic";

export default function AboutPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AboutPageComponent />
    </Suspense>
  );
}
