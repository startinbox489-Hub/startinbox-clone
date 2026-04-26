'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function SuccessPopup() {
	const [proceed, setProceed] = useState<string>('NEXT');
	const router = useRouter();
	const handleOnClick = () => {
		setProceed('Loading Analysis...');
		router.push('/analysis?i=1');
	};
	return (
		<div className="p-12 text-center max-w-lg mx-auto">
			<div className="mb-6 text-6xl">
				<span role="img" aria-label="Rocket">
					🚀
				</span>
			</div>
			<h3 className="text-3xl font-extrabold text-gray-900 mb-4">
				We&apos;ve Matched You With a PM
			</h3>
			<p className="text-lg text-gray-600">
				You&apos;re all set! Review the onboarding message sent to your
				email/WhatsApp to kick things off.
			</p>
			<button
				className="px-6 py-2 mt-8 bg-blue-600 text-white rounded-md"
				onClick={handleOnClick}
			>
				{proceed}
			</button>
		</div>
	);
}
