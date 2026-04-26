'use client';

import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

export default function GoogleAnalytics() {
	const pathname = usePathname();

	useEffect(() => {
		const url = pathname + window.location.search;

		if ('gtag' in window) {
			window.gtag('config', process.env.NEXT_PUBLIC_GA_ID!, {
				page_path: url,
			});
		}
	}, [pathname]);

	return null;
}
