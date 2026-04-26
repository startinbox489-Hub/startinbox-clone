import React, { Suspense } from 'react';

import SignupForm from './SignupForm';
export const dynamic = 'force-dynamic';

export default function SignupPage() {
	return (
		<Suspense fallback={<div>Loading...</div>}>
			<div className="min-h-screen relative flex flex-col">
				{/* Background Gradient Container */}
				<div
					className="absolute inset-0 z-0"
					style={{
						background:
							'linear-gradient(to bottom right, #f8fafc, #6D28D9, #A78BFA)',
						// opacity: 0.3
					}}
				></div>

				{/* Main Content Container */}
				<div className="relative z-10 flex flex-col flex-grow">
					{/* Signup Form Section */}
					<div className="flex-grow flex items-center justify-center p-4">
						<SignupForm />
					</div>
				</div>
			</div>
		</Suspense>
	);
}
