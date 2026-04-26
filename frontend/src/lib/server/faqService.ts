import 'server-only';

import { faqsData } from '@/staticData/faqData';
import { FAQItem } from '@/types/faq';
import serverConfig from '../config/private';

export default class FAQService {
	static async getFAQs(): Promise<FAQItem[]> {
		try {
			const response = await fetch(
				`${await serverConfig('BACKEND_BASE_URL')}/api/v1/faqs`,
				{
					method: 'GET',
					next: { revalidate: 7200 }, // every 2 hours
				},
			);
			const data: FAQItem[] = (await response.json()).data;
			if (response.status !== 200) {
				return faqsData;
			}
			return data;
		} catch (error) {
			console.error('error retrieving faqs: ', error);
			return faqsData;
		}
	}
}
