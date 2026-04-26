import 'server-only';

import serverConfig from '../config/private';
import {
	AddOnsServicesI,
	APIAddOnsServicesI,
} from '@/components/Landing/AddOnServicesSection/interface';

export default class AddOnService {
	static async getAddOns(): Promise<AddOnsServicesI[]> {
		try {
			const response = await fetch(
				`${await serverConfig('BACKEND_BASE_URL')}/api/v1/adds-on-services`,
				{
					method: 'GET',
					next: { revalidate: 3600 }, // every 1 hour
				},
			);
			const data: APIAddOnsServicesI = await response.json();
			if (response.status !== 200) {
				return [];
			}
			return data.data.map((addOn, idx) => {
				return {
					...addOn,
					selectedPriceIndex: idx,
					prices: addOn.prices.map((price, idx2) => ({
						...price,
						selectedPriceIndex: idx2,
					})),
				};
			});
		} catch (error) {
			console.error('error retrieving faqs: ', error);
			return [];
		}
	}
}
