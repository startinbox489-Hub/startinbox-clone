/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

export default function MetaPageView() {
	const pathname = usePathname();

	useEffect(() => {
		if (!(window as any).fbq) return;
		(window as any).fbq('track', 'PageView');
	}, [pathname]);

	return null;
}
