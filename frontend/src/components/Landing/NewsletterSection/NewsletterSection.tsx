'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { track } from '@/lib/client/metaPixel';

const NewsletterSection = () => {
	const [email, setEmail] = useState('');
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [message, setMessage] = useState('');
	const [showPopup, setShowPopup] = useState(false);

	useEffect(() => {
		let timer: NodeJS.Timeout | null = null;
		if (showPopup) {
			timer = setTimeout(() => {
				setShowPopup(false);
			}, 2000);
		}

		return () => {
			if (timer) {
				clearTimeout(timer);
			}
		};
	}, [showPopup]);

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setIsSubmitting(true);
		setMessage('');
		setShowPopup(false);

		try {
			const response = await fetch('/api/v1/newsletter', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ email }),
			});
			const data = await response.json();

			if (response.status === 201) {
				// Successful subscription
				setMessage(
					'You have successfully subscribed to Startin Box newsletter',
				);
				setEmail('');
				setShowPopup(true);
				track('Subscribe', {
					source: 'landing_page_footer',
				});
				return;
			} else if (response.status === 409) {
				// Email is already subscribed
				setMessage('Already subscribed to Startin Box newsletter');
				setEmail('');
				setShowPopup(true);
				return;
			} else {
				// Other errors
				setMessage(data.message || 'Something went wrong. Please try again.');
			}
		} catch (_) {
			setMessage('An error occurred. Please check your network and try again.');
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<section className="bg-white py-12 px-6 sm:px-10 lg:px-20">
			<div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
				{/* Newsletter Text */}
				<div className="mb-6 md:mb-0 md:w-1/2 text-center md:text-left">
					<h2 className="text-2xl font-bold text-gray-800 mb-1">
						Join our newsletter
					</h2>
					<p className="text-gray-600">
						We’ll send you a nice letter once per week. No spam.
					</p>
				</div>

				{/* Newsletter Form */}
				<div className="w-full md:w-1/2 flex justify-center md:justify-end">
					<form
						onSubmit={handleSubmit}
						className="flex flex-col sm:flex-row w-full max-w-md"
					>
						<input
							type="email"
							id="email"
							placeholder="Enter your email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							className="w-full text-blue-950 sm:w-2/3 p-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500 mb-3 sm:mb-0 sm:mr-3"
							required
							name="email"
							autoComplete="email"
						/>
						<button
							type="submit"
							className="w-full sm:w-1/3 py-3 rounded-lg text-white font-semibold transition-transform transform hover:scale-105"
							disabled={isSubmitting}
							style={{
								background: 'linear-gradient(to right, #6D28D9, #A78BFA)',
							}}
						>
							{isSubmitting ? 'Subscribing...' : 'Subscribe'}
						</button>
					</form>
				</div>
			</div>

			{/* Popup section for success or already-subscribed */}
			{showPopup && (
				<div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50 transition-opacity duration-300">
					<div className="relative bg-white p-8 rounded-lg shadow-xl text-center max-w-sm w-full">
						<button
							onClick={() => setShowPopup(false)}
							className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 focus:outline-none"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								className="h-6 w-6"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</button>
						<div className="flex flex-col items-center justify-center">
							<div className="mb-4">
								<Image
									src="/startinbox-newsletter-popup-logo.png"
									alt="Success icon"
									width={100}
									height={100}
									className="mx-auto"
								/>
							</div>
							<h3 className="text-xl md:text-2xl font-bold text-gray-800">
								{message}
							</h3>
						</div>
					</div>
				</div>
			)}
		</section>
	);
};

export default NewsletterSection;
