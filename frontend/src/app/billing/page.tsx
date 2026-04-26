import { redirect } from 'next/navigation';
import { IBillingProps } from './verify/components/interface';

export default async function Billing({ searchParams }: IBillingProps) {
	const newParams = new URLSearchParams();

	Object.entries(await searchParams).forEach(([key, value]) => {
		if (Array.isArray(value)) {
			value.forEach((v) => newParams.append(key, v));
		} else if (value !== undefined) {
			newParams.append(key, value);
		}
	});

	redirect(`/billing/verify?${newParams.toString()}`);
}
