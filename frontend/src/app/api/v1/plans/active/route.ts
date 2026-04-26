import { proxyWithAuth } from '@/lib/server/apiProxy';
import { NextResponse } from 'next/server';

export async function GET(req: Request) {
	try {
		const response = await proxyWithAuth('/api/v1/subscription-plans/active', {
			method: 'GET',
			headers: { 'Content-Type': 'application/json' },
		});
		const cookies = response.headers.getSetCookie();
		const headers = new Headers();
		headers.append('Set-Cookie', cookies[0]); // access
		headers.append('Set-Cookie', cookies[1]); // refresh
		const data = await response.json();

		return NextResponse.json(
			{
				...data,
				...(response.status === 401 && { status: 'signin required' }),
			},
			{ headers, status: response.status },
		);
	} catch (error) {
		console.error('proxy error fethcing active user plans:', error);
		return NextResponse.json(
			{ message: 'Internal Server Error', data: {} },
			{ status: 500 },
		);
	}
}
