import { Mail, XCircle } from 'lucide-react';
import Link from 'next/link';
import { IPaymentFailedProps } from './interface';

export default function PaymentFailed({
	verifyStatus,
	errorMessage,
}: IPaymentFailedProps) {
	const errorMessages =
		verifyStatus === 'card_declined'
			? 'Your card was declined. Please try another payment method.'
			: verifyStatus === 'insufficient_funds'
				? 'Insufficient funds. Please ensure your card has available funds.'
				: verifyStatus === 'authentication_failed'
					? 'Authentication failed. Please complete the 3D Secure verification.'
					: 'There was an issue processing your payment. Please try again.';

	return (
		<div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center p-4">
			<div className="max-w-md w-full">
				<div className="bg-white rounded-2xl shadow-xl overflow-hidden">
					<div className="bg-gradient-to-r from-red-500 to-pink-500 p-8 text-center">
						<div className="flex justify-center mb-4">
							<div className="bg-white/20 rounded-full p-3 backdrop-blur-sm">
								<XCircle className="w-20 h-20 text-white" />
							</div>
						</div>
						<h1 className="text-3xl font-bold text-white mb-2">
							Payment Failed
						</h1>
						<p className="text-red-100 text-lg">
							We couldn&apos;t process your payment
						</p>
					</div>

					<div className="p-8">
						<div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
							<p className="text-red-800 text-sm">{errorMessage}</p>
						</div>

						<div className="mb-8">
							<h3 className="font-semibold text-gray-900 mb-3">
								Things you can try:
							</h3>
							<ul className="space-y-3">
								<li className="flex items-start gap-3">
									<div className="bg-blue-100 rounded-full p-1 mt-0.5">
										<span className="block w-4 h-4 text-xs text-blue-600 font-bold text-center">
											1
										</span>
									</div>
									<p className="text-sm text-gray-600">
										Use a different payment method or card
									</p>
								</li>
								<li className="flex items-start gap-3">
									<div className="bg-blue-100 rounded-full p-1 mt-0.5">
										<span className="block w-4 h-4 text-xs text-blue-600 font-bold text-center">
											2
										</span>
									</div>
									<p className="text-sm text-gray-600">
										Contact your bank to ensure the card is enabled for online
										transactions
									</p>
								</li>
								<li className="flex items-start gap-3">
									<div className="bg-blue-100 rounded-full p-1 mt-0.5">
										<span className="block w-4 h-4 text-xs text-blue-600 font-bold text-center">
											3
										</span>
									</div>
									<p className="text-sm text-gray-600">
										Check if you have sufficient funds in your account
									</p>
								</li>
							</ul>
						</div>

						<div className="flex flex-wrap sm:flex-row gap-4">
							<button
								onClick={() => window.location.reload()}
								className="flex-1 inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
							>
								Try Again
							</button>
							<Link
								href={'/pricing'}
								className="flex-1 inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
							>
								Back
							</Link>
							<a
								href="mailto:support@startinbox.tech"
								className="flex-1 inline-flex justify-center items-center px-2 py-1 border-2 border-gray-300 text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200"
							>
								<Mail className="w-5 h-5 mr-2" /> support@startinbox.tech
							</a>
						</div>

						<p className="flex flex-col items-center justify-center text-xs text-center text-gray-500 mt-6">
							Need help?{' '}
							<a
								href="mailto:contact@startinbox.tech"
								className="text-lg text-gray-500 font-medium hover:text-indigo-200 transition duration-200 flex items-center"
							>
								Contact our support team
							</a>
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}
