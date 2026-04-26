/* eslint-disable @typescript-eslint/no-explicit-any */
import { v4 as uuidv4 } from 'uuid';

export const track = (
	event: string,
	params?: Record<string, any>,
): string | undefined => {
	if (typeof window === 'undefined') return;
	if (!(window as any).fbq) return;

	const event_id = uuidv4();

	(window as any).fbq('track', event, {
		...params,
		event_id,
	});

	return event_id;
};
