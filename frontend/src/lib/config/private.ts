'use server';

const privateValues = {
	GOOGLE_CLIENT_ID: (() => {
		const val = process.env.GOOGLE_CLIENT_ID;
		if (!val)
			throw new Error('❌ Config Error: GOOGLE_CLIENT_ID is not defined.');
		return val;
	})(),

	GOOGLE_CLIENT_SECRET: (() => {
		const val = process.env.GOOGLE_CLIENT_SECRET;
		if (!val)
			throw new Error('❌ Config Error: GOOGLE_CLIENT_SECRET is not defined.');
		return val;
	})(),

	BACKEND_BASE_URL: (() => {
		const val = process.env.BACKEND_BASE_URL;
		if (!val)
			throw new Error('❌ Config Error: BACKEND_BASE_URL is not defined.');
		return val;
	})(),
};

export type PrivateConfigKeys = keyof typeof privateValues;

export default async function serverConfig(
	key: PrivateConfigKeys,
	defaultValue?: (typeof privateValues)[PrivateConfigKeys],
): Promise<(typeof privateValues)[PrivateConfigKeys]> {
	return privateValues[key] ?? defaultValue!;
}
// export default class PrivateConfid {
// 	static readonly values = privateValues;

// 	static get<K extends PrivateConfigKeys>(
// 		key: K,
// 		defaultValue?: (typeof privateValues)[K],
// 	): (typeof privateValues)[K] {
// 		return privateValues[key] ?? defaultValue!;
// 	}
// }
