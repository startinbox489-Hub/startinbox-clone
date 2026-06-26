import PricingSection from "@/components/Landing/Pricing/Pricing";
import PricingService from "@/lib/server/pricingService";
import CreditSubscription from "@/components/Landing/Pricing/CreditSubscription/CreditSubscription";
export const dynamic = "force-dynamic";

export default async function PricingPage() {
  const plans = await PricingService.getPricingPlans();

  return (
    <>
      <PricingSection
        heading="SIMPLE AND TRANSPARENT PRICING"
        subheading="Choose a plan that matches your launch stage, there are no hidden fees, and you can cancel anytime."
        plans={plans}
      />
      <CreditSubscription plans={plans} />
    </>
  );
}
