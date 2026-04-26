'use server';

import { cookies } from 'next/headers';
import * as jose from 'jose';

import { ApiUserData } from '@/types/users.types';
import PublicConfig from '../config/public';

async function getUserData(): Promise<ApiUserData> {
	try {
		const cookieStore = cookies();

		const accessToken = (await cookieStore).get('access_token')?.value || '';
		const refreshToken = (await cookieStore).get('refresh_token')?.value || '';

		if (!accessToken || accessToken === '') {
			return { message: 'Not signed in', user: null };
		}

		const response = await fetch(
			`${PublicConfig.get('BASE_URL')}/api/v1/auth/user/me`,
			{
				headers: {
					'Content-Type': 'application/json',
					Authorization: accessToken ? `Bearer ${accessToken}` : '',
				},
				credentials: 'include',
				cache: 'no-store',
			},
		);

		const data = await response.json();

		if (response.status === 401) {
			if (!refreshToken || refreshToken === '') {
				return { message: data.message, user: null };
			}
			const refreshRes = await fetch(
				`${PublicConfig.get('BASE_URL')}/api/v1/auth/refresh-tokens`,
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						'X-REFRESH-TOKEN': refreshToken,
					},
				},
			);

			const data2 = await refreshRes.json();

			if (refreshRes.ok) {
				const { access_token: newAccess } = await refreshRes.json();
				const new_refresh_token = response.headers.get(
					'x-refresh-token',
				) as string;

				(await cookieStore).set('access_token', newAccess, {
					httpOnly: true,
					secure: true,
					sameSite: 'lax',
					path: '/',
				});
				(await cookieStore).set('refresh_token', new_refresh_token, {
					httpOnly: true,
					secure: true,
					sameSite: 'lax',
					path: '/',
				});

				// Retry original request with new token
				const response2 = await fetch(
					`${PublicConfig.get('BASE_URL')}/v1/auth/user/me`,
					{
						headers: {
							'Content-Type': 'application/json',
							Authorization: accessToken ? `Bearer ${accessToken}` : '',
						},
						credentials: 'include',
						cache: 'no-store',
						method: 'GET',
					},
				);

				const data3 = await response2.json();
				return { message: data2.message, user: data3.data.data || null };
			}

			return { message: data2.message, user: data.data || null };
		}
		if (response.status === 500) {
			return { message: data.message, user: null };
		}
		return { message: data.message, user: data.data };
	} catch (error) {
		console.error('error fetching user data: ', error);
		return { message: 'error fetching user data', user: null };
	}
}

async function getUserFromCookie(email: boolean = true) {
	const token = (await cookies()).get('access_token')?.value;
	if (!token) return null;

	try {
		const decoded = jose.decodeJwt(token);
		if (email) return decoded.email as string;
		return decoded;
	} catch {
		return null;
	}
}

export { getUserData, getUserFromCookie };
