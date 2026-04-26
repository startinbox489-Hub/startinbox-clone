'use server';

import { proxyWithAuth } from '@/lib/server/apiProxy';
import { NextResponse } from 'next/server';

export async function GET(req: Request) {
	try {
		const response = await proxyWithAuth('/api/v1/auth/user/me');
		const data = await response.json();

		const cookies = response.headers.getSetCookie();
		// console.log('cookies: ', cookies);
		const headers = new Headers();
		headers.append('Set-Cookie', cookies[0]); // access
		headers.append('Set-Cookie', cookies[1]); // refresh
		// console.log('data: ', data);
		return NextResponse.json(
			{
				...data,
				...(response.status === 401 && { status: 'signin required' }),
			},
			{ headers, status: response.status },
		);
	} catch (error) {
		console.error('Error in proxy get user data: ', error);
		return NextResponse.json(
			{
				data: null,
				status: 'error',
				message: 'Internal Server Error',
			},
			{ status: 500 },
		);
	}
}
