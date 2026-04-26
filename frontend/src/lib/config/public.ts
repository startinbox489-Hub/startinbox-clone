const publicValues = {
	BASE_URL: (() => {
		const {
			NODE_ENV,
			API_BASE_URL,
			API_BASE_URL_STAGING,
			NEXT_PUBLIC_API_BASE_URL_PROD,
		} = process.env;

		let url: string | undefined;

		switch (NODE_ENV) {
			case 'development':
				url = API_BASE_URL;
				break;
			case 'test':
				url = API_BASE_URL_STAGING ?? API_BASE_URL;
				break;
			case 'production':
				url = NEXT_PUBLIC_API_BASE_URL_PROD ?? API_BASE_URL;
				break;
			default:
				throw new Error(`❌ Config Error: Unsupported NODE_ENV "${NODE_ENV}"`);
		}

		if (!url) {
			throw new Error(
				`❌ Config Error: NEXT_PUBLIC_API_BASE_URL not defined for NODE_ENV="${NODE_ENV}"`,
			);
		}

		return url;
	})(),
};

export type PublicConfigKeys = keyof typeof publicValues;

export default class PublicConfig {
	static readonly values = publicValues;

	static get<K extends PublicConfigKeys>(
		key: K,
		defaultValue?: (typeof publicValues)[K],
	): (typeof publicValues)[K] {
		return publicValues[key] ?? defaultValue!;
	}
}
