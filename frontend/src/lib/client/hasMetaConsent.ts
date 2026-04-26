export function hasMetaConsent() {
	if (typeof window === 'undefined') return false;

	try {
		const stored = localStorage.getItem('startinbox_cookieConsent');
		if (!stored) return false;

		const { value, expiry } = JSON.parse(stored);
		return value === true && expiry > Date.now();
	} catch {
		return false;
	}
}
