import { ApiPricingPlan } from "@/types/pricingPlan.type";
import { AddOnsServicesI } from "../AddOnServicesSection/interface";

export interface ValidateIdeaSectionProps {
  plans: ApiPricingPlan[];
  addOns: AddOnsServicesI[];
  email?: string | null;
}

export interface IdeaModelI {
  id: string;
  user_id: string;
  prompt: string;
  idea_validation: string;
  idea_score?: number | null;
  lean_canvas?: {
    channels?: string;
    cost_structure?: string;
    customer_segments?: string;
    key_metrics?: string;
    problem?: string;
    revenue_streams?: string;
    solution?: string;
    unfair_advantage?: string;
    unique_value_proposition?: string;
  } | null;
  ideal_customer_persona?: {
    age_range?: string;
    goals?: string;
    name?: string;
    occupation?: string;
    pain_points?: string;
  } | null;
  suggested_startup_names?: string[] | null;
  monetization_models?: string[] | null;
  website_hero?: {
    features?: string[];
    headline?: string;
    subheadline?: string;
  } | null;
  blog_posts?: Array<{ outline?: string[]; title?: string }> | null;
  twitter_posts?: string[] | null;
  elevator_pitch_slide?: { bullet_points?: string[]; headline?: string } | null;
  go_to_market_strategy_outline?: string | null;
}

export interface TempIdeaT {
  tempIdea: string;
  planIdx: number;
}

export interface IdeaStoreStateI {
  ideas: IdeaModelI[];
  pushIdea: (idea: IdeaModelI) => void;
  popIdea: (ideadId: string) => void;
  clearIdeas: () => void;

  tempIdea: TempIdeaT | undefined;
  clearTemIdea: () => void;
  addTempIdea: (newTempIdea: TempIdeaT) => void;
}

export interface TempIdeaI {
  selectedAddOns: {
    id: string;
    amount: number;
    unit: string;
  }[];
  tempIdea: string;
  planIdx: number;
}
