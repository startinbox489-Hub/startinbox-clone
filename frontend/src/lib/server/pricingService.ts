import "server-only";

import serverConfig from "../config/private";

import { ApiPricingPlan, AppPricingPlan } from "@/types/pricingPlan.type";

export default class PricingService {
  static async getPricingPlans(): Promise<AppPricingPlan[]> {
    try {
      const response = await fetch(
        `${await serverConfig("BACKEND_BASE_URL")}/api/v1/subscription-plans`,
        {
          next: { revalidate: 3600 }, // Revalidate data every hour
          method: "GET",
        },
      );
      if (![200, 201].includes(response.status)) {
        const data = await response.json();
        console.error("error fetching plans: ", data);

        return [];
      }
      const data: ApiPricingPlan[] = (await response.json()).data;
      const plansArray = data.map((plan): AppPricingPlan => {
        return {
          id: plan.id,
          name: plan.name,
          price: plan.price,
          description: plan.description,
          idx: plan.idx,
          features: plan.features.map((feature) => {
            return {
              name: feature.name.replace(/_/g, " "),
            };
          }),
          type: plan.type,
          credits: plan.credits,
          flutterwave_plan_id: plan.flutterwave_plan_id,
          buttonText: plan.idx === 0 ? "Get Started" : "Choose Plan",
          buttonLink: `/signin?plan=${plan.idx}`,
          is_popular: plan.is_popular,
        };
      });
      return plansArray;
    } catch (error) {
      console.error("error fetching pricing plans: ", error);
      return [];
    }
  }
}
