export type ApiFeature = {
  name: string;
  value?: number | null;
};
export const TPricingType = Object.freeze({
  ONEOFF: "oneoff",
  REOCCURRING: "reoccurring",
});

export type ApiPricingPlan = {
  id: string;
  name: string;
  price: number;
  description: string;
  idx: number;
  features: ApiFeature[];
  is_popular: boolean;
  type: (typeof TPricingType)[keyof typeof TPricingType];
  credits: number;
  flutterwave_plan_id: number;
};

export type AppPricingPlan = ApiPricingPlan & {
  buttonText: string;
  buttonLink: string;
};

export interface ValidationPricingSectionProps {
  plans: AppPricingPlan[];
}
