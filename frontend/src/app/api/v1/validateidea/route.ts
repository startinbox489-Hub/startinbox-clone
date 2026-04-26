'use server';

import { proxyWithAuth } from '@/lib/server/apiProxy';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
	try {
		const body = await req.json();
		const response = await proxyWithAuth('/api/v1/startup-ideas', {
			method: 'POST',
			body: JSON.stringify(body),
			headers: { 'Content-Type': 'application/json' },
		});
		const data = await response.json();
		// console.log('data: ', data);

		if ([422, 417, 402].includes(response.status)) {
			let message: string = data.message;
			console.log('data: ', data);
			if (data.data?.msg?.startsWith('Value error')) {
				message = data.data?.msg?.substring(12);
			}
			return NextResponse.json(
				{
					message: message.replace(/_/g, ' '),
					idea: null,
					status: 'error',
				},
				{ status: response.status },
			);
		}

		if (response.status > 499) {
			console.log('data: ', data);
			return NextResponse.json(
				{
					message: 'Internal Server Error. Contact Us with the code #vi001',
					status: 'error',
					idea: null,
				},
				{ status: response.status },
			);
		}

		const cookies = response.headers.getSetCookie();
		// console.log('cookies: ', cookies);
		const headers = new Headers();
		headers.append('Set-Cookie', cookies[0]); // access
		headers.append('Set-Cookie', cookies[1]); // refresh
		// console.log('data: ', data);

		return NextResponse.json(
			{
				message: data.message,
				status: data.status,
				idea: data.data.validation,
				idx: data.data.idx,
			},
			{ status: response.status, headers },
		);
	} catch (error) {
		console.error('idea validation proxy error:', error);
		return NextResponse.json(
			{ message: 'Internal Server Error', idea: null, status: 'error' },
			{ status: 500 },
		);
	}
}
