import { DefaultSession } from 'next-auth';

declare module 'next-auth' {
	interface Session {
		user: {
			/** default user props */
			name?: string | null;
			email?: string | null;
			image?: string | null;
		} & DefaultSession['user'];

		/** custom tokens we added */
		idToken?: string;
		accessToken?: string;
	}

	interface JWT {
		idToken?: string;
		accessToken?: string;
	}
}
