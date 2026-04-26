'use client';

import React from 'react';
import { Check } from 'lucide-react';

interface PaymentCardProps {
	statusText?: string;
	validationMessage?: string;
	showLoadingSpinner?: boolean;
}

const spinnerStyle = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.animate-spin-custom {
  animation: spin 1.2s cubic-bezier(0.68, -0.55, 0.27, 1.55) infinite; /* More bouncy spin */
}
`;

const PaymentReceivedCard = ({
	statusText = 'Payment Received',
	validationMessage = 'Startin Box is validating your idea...',
	showLoadingSpinner = true,
}: PaymentCardProps) => {
	return (
		<div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
			<style dangerouslySetInnerHTML={{ __html: spinnerStyle }} />

			{/* Confirmation Card Container */}
			<div
				className={`
                w-full max-w-sm 
                bg-white rounded-2xl shadow-2xl 
                p-8 text-center
                transform transition-all duration-300
            `}
			>
				{/* Checkmark Icon Container */}
				<div className="flex justify-center mb-6">
					<div className="bg-blue-600 rounded-full p-3 shadow-lg shadow-blue-500/50">
						{/* Checkmark Icon */}
						<Check className="w-12 h-12 text-white font-bold" strokeWidth={4} />
					</div>
				</div>

				{/* Main Status Text */}
				<h1 className="text-3xl font-extrabold text-gray-900 mb-2 tracking-tight">
					{statusText}
				</h1>

				{/* Secondary Validation Message */}
				<p className="text-base text-purple-600 font-medium mb-8">
					{validationMessage}
				</p>

				{/* Loading Spinner Area */}
				{showLoadingSpinner && (
					<div className="flex justify-center">
						<svg
							className="w-8 h-8 text-purple-600 animate-spin-custom"
							xmlns="http://www.w3.org/2000/svg"
							fill="none"
							viewBox="0 0 24 24"
						>
							<circle
								className="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								strokeWidth="4"
							></circle>
							<path
								className="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
					</div>
				)}
			</div>
		</div>
	);
};

// 	return (
// 		<PaymentReceivedCard
// 			statusText="Payment Received"
// 			validationMessage="Startin Box is validating your idea..."
// 			showLoadingSpinner={true}
// 		/>
// 	);

export default PaymentReceivedCard;
