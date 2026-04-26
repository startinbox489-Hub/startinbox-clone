import { ApiPricingPlan } from '@/types/pricingPlan.type';
import { create } from 'zustand';

export interface PlansStoreStateI {
	plans: ApiPricingPlan[];
	setPlane: (plans: ApiPricingPlan[]) => void;
	clearPlans: () => void;
	selectedPlan: number;
	setSelectedPlan: (plan: number) => void;
	clearSelectedPlan: () => void;
}

const usePlansStoreState = create<PlansStoreStateI>((set) => ({
	plans: [],
	setPlane: (plans) => set({ plans }),
	clearPlans: () => set({ plans: [] }),
	selectedPlan: 0,
	setSelectedPlan: (selectedPlan: number) => set({ selectedPlan }),
	clearSelectedPlan: () => set({ selectedPlan: 0 }),
}));

export default usePlansStoreState;
