'use server';

import { proxyWithAuth } from '@/lib/server/apiProxy';
import { NextResponse } from 'next/server';

export async function GET(_: Request) {
	try {
		const response = await proxyWithAuth('/api/v1/auth/user/me', {
			method: 'GET',
		});
		const data = await response.json();
		const cookies = response.headers.getSetCookie();
		const headers = new Headers();
		headers.append('Set-Cookie', cookies[0]);
		headers.append('Set-Cookie', cookies[1]);

		if (!response.ok) {
			return NextResponse.json(
				{ status: 'error', message: 'Fetch user data failed', data: null },
				{ status: response.status, headers },
			);
		}

		return NextResponse.json(
			{ message: 'User data fetched successfully', ...data },
			{ headers, status: response.status },
		);
	} catch (error) {
		console.error('Fetch user data failed:', error);
		return NextResponse.json(
			{ status: 'error', message: 'Fetch user data failed', data: null },
			{ status: 500 },
		);
	}
}
