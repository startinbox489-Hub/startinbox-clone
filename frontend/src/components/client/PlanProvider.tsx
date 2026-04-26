'use client';

import { useAuthStore } from '@/store/authStore';
import { usePassedEmail } from '@/store/emailStore';
import usePlansStoreState from '@/store/planStore';
import { AppPricingPlan } from '@/types/pricingPlan.type';
import { UserModel } from '@/types/users.types';
import { useEffect } from 'react';

export interface PlansProviderProps {
	plans: AppPricingPlan[];
	user?: UserModel;
	email?: string | null;
}

// receives the initial user data from a Server Component.
export default function PlansProvider({
	plans,
	user,
	email,
}: PlansProviderProps) {
	const setPlan = usePlansStoreState((state) => state.setPlane);
	const setUser = useAuthStore((state) => state.signin);
	const setEmail = usePassedEmail((state) => state.setEmail);

	useEffect(() => {
		if (plans) {
			setPlan(plans);
		}
		if (email) {
			setEmail(email);
		}
		if (user) {
			setUser(user);
		}
	}, [email, plans, setEmail, setPlan, setUser, user]);

	return null; // render nothing visible.
}
