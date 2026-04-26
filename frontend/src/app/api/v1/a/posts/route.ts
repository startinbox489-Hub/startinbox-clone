'use server';

import { proxyWithAuth } from '@/lib/server/apiProxy';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
	try {
		const body = await req.json();
		console.log('posting...: ');

		const response = await proxyWithAuth(`/api/v1/a/posts`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			credentials: 'include',
			body: JSON.stringify(body),
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
		console.error('blog creation proxy error:', error);
		return NextResponse.json(
			{ message: 'Internal Server Error', data: {} },
			{ status: 500 },
		);
	}
}
