import { ApiFeature, TPricingType } from '@/types/pricingPlan.type';

export interface IPricingCardProps {
	plan: {
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
		period: string;
		buttonText: string;
		buttonLink: string;
	};
	setSelectedPlan: (plan: TSelectedPlan) => void;
}

export type TSelectedPlan = {
	id: string;
	name: string;
	price: number;
	idx: number;
	credits: number;
	flutterwave_plan_id: number;
};
