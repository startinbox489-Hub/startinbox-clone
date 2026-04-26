import React from 'react';
import { Suspense } from 'react';

import SigninForm from '@/app/signin/SigninForm';
export const dynamic = 'force-dynamic';

export default async function SigninPage({
	searchParams,
}: {
	searchParams: Promise<{ plan?: string; next?: string }>;
}) {
	return (
		<Suspense fallback={<>Loading Signin...</>}>
			<div
				className="min-h-screen relative flex flex-col items-center justify-center p-4"
				style={{
					background:
						'linear-gradient(to bottom right, #f8fafc, #6D28D9, #A78BFA)',
				}}
			>
				<div className="relative z-10 w-full flex-grow flex items-center justify-center">
					<SigninForm searchParams={searchParams} />
				</div>
			</div>
		</Suspense>
	);
}
