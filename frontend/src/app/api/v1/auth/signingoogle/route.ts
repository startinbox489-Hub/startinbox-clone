'use server';

import ConfigService from '@/lib/config';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
	try {
		const body = await req.json();
		const response = await fetch(
			`${await ConfigService.get('BASE_URL')}/api/v1/auth/signin/google`,
			{
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(body),
				method: 'POST',
				credentials: 'include',
			},
		);
		const data = await response.json();
		const access_token = data?.data?.token?.access_token;
		const refresh_token = response.headers.get('x-refresh-token');

		if (response.status === 417) {
			return NextResponse.json(
				{
					status: 'error',
					message: data.message,
					user: null,
				},
				{ status: response.status },
			);
		}
		if (response.status > 499) {
			return NextResponse.json(
				{
					message: 'Internal Server Error. Contact Us with the code #su005',
					status: 'error',
					user: null,
				},
				{ status: 500 },
			);
		}

		const headers = new Headers();
		// Store tokens in httpOnly cookies
		headers.append(
			'Set-Cookie',
			`access_token=${access_token}; Path=/; HttpOnly; Secure; SameSite=Lax`,
		);
		headers.append(
			'Set-Cookie',
			`refresh_token=${refresh_token}; Path=/; HttpOnly; Secure; SameSite=Lax`,
		);

		return NextResponse.json(
			{ message: data.message, user: data.data.user, status: 'success' },
			{ status: response.status, headers },
		);
	} catch (error) {
		console.error('proxy Error signing in user via google :', error);
		return NextResponse.json(
			{ message: 'Internal Server Error', user: null, status: 'error' },
			{ status: 500 },
		);
	}
}
