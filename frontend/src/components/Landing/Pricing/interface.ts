import { AppPricingPlan } from "@/types/pricingPlan.type";

export interface IPricingProps {
  heading: string;
  subheading: string;
  plans: AppPricingPlan[];
}
