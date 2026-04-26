'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
	Mail,
	Loader2,
	CheckCircle,
	XCircle,
	HeartHandshake,
} from 'lucide-react';
import {
	ConfirmationModalProps,
	LayoutProps,
	UnsubscribeFormProps,
} from '@/types/newsletterTypes';

const REASONS = [
	'Too many emails',
	'Content is not relevant to me',
	'I never signed up for this newsletter',
	'I found the content elsewhere',
	'Other (please specify)',
];

const UnsubscribeForm = ({ initialHash }: UnsubscribeFormProps) => {
	const [newsletterHash, setNewsletterHash] = useState('');
	const [isConfirming, setIsConfirming] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [status, setStatus] = useState<string | null>(null); // 'success' | 'error' | null
	const [selectedReason, setSelectedReason] = useState('');
	const [otherReasonText, setOtherReasonText] = useState('');

	// Effect to grab the hash from the prop once the component mounts
	useEffect(() => {
		if (initialHash && typeof initialHash === 'string') {
			setNewsletterHash(initialHash);
		}
	}, [initialHash]);

	// Handler for the unsubscribe action
	const handleUnsubscribe = useCallback(async () => {
		if (!newsletterHash) return;

		// Prepare the final payload
		const finalReason =
			selectedReason === 'Other (please specify)'
				? otherReasonText
				: selectedReason;

		if (finalReason.length > 255) {
			setStatus('reason-length');
			return;
		}

		setIsLoading(true);
		setStatus(null);

		const payload = {
			newsletter_hash: newsletterHash,
			// Only include the reason if a selection was made
			...(finalReason && { reason: finalReason }),
		};

		try {
			// API call with Exponential Backoff
			let response = null;
			let attempt = 0;
			const maxAttempts = 3;

			while (attempt < maxAttempts) {
				attempt++;
				try {
					response = await fetch('/api/v1/newsletter', {
						method: 'PATCH',
						headers: {
							'Content-Type': 'application/json',
						},
						body: JSON.stringify(payload),
					});

					if (response.status === 404) {
						setStatus('not-subscribed');
						return;
					}
					if (response.ok || response.status < 500) {
						break; // Break on success or client-side errors (4xx)
					}

					// Retry on server errors (5xx)
					if (attempt < maxAttempts) {
						const delay = Math.pow(2, attempt) * 1000; // 2s, 4s, 8s
						await new Promise((resolve) => setTimeout(resolve, delay));
					}
				} catch (fetchError) {
					// If fetch fails completely (e.g., network error), retry
					if (attempt === maxAttempts) {
						throw fetchError;
					}
					const delay = Math.pow(2, attempt) * 1000;
					await new Promise((resolve) => setTimeout(resolve, delay));
				}
			}

			if (!response || !response.ok) {
				// Handle final API error
				const status = response ? response.status : 'N/A';
				const statusText = response ? response.statusText : 'Network Error';
				throw new Error(`API error: ${status} ${statusText}`);
			}

			// Successful unsubscribe
			setStatus('success');
		} catch (error) {
			console.error('Unsubscribe failed:', error);
			setStatus('error');
		} finally {
			setIsLoading(false);
			setIsConfirming(false); // Close confirmation modal if open
		}
	}, [newsletterHash, selectedReason, otherReasonText]);

	// --- Invalid Hash State Display ---
	if (!newsletterHash) {
		return (
			<Layout>
				<div className="text-center p-8 bg-white shadow-xl rounded-xl">
					<XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
					<h2 className="text-2xl font-semibold text-gray-800">Invalid Link</h2>
					<p className="text-gray-600">
						The unsubscribe link is missing or invalid. Please check the URL.
					</p>
				</div>
			</Layout>
		);
	}

	// --- Success State Display ---
	if (status === 'success') {
		return (
			<Layout>
				<div className="text-center p-8 bg-white shadow-2xl rounded-xl border border-green-200">
					<CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4 animate-bounce" />
					<h2 className="text-3xl font-bold text-gray-800 mb-2">
						You&apos;re Unsubscribed!
					</h2>
					<p className="text-lg text-gray-600">
						We&apos;ve successfully removed your email from our list. You will
						no longer receive our newsletter.
					</p>
					{selectedReason && (
						<div className="mt-6 p-3 bg-green-50 text-green-700 rounded-lg text-sm">
							Thank you for providing feedback:{' '}
							<strong>
								{selectedReason === 'Other (please specify)'
									? otherReasonText
									: selectedReason}
							</strong>
						</div>
					)}
					<div className="mt-8 text-sm text-gray-500">
						If this was a mistake, please reach out to our support team.
					</div>
				</div>
			</Layout>
		);
	}

	// --- Error State Display ---
	if (status === 'error') {
		return (
			<Layout>
				<div className="text-center p-8 bg-white shadow-2xl rounded-xl border border-red-200">
					<XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
					<h2 className="text-3xl font-bold text-gray-800 mb-2">
						Unsubscribe Failed
					</h2>
					<p className="text-lg text-gray-600">
						There was an issue processing your request. Please try again later
						or contact support.
					</p>
					<p className="mt-4 text-sm text-gray-500">
						Error code: {newsletterHash}
					</p>
				</div>
			</Layout>
		);
	}
	if (status === 'not-subscribed') {
		return (
			<Layout>
				<div className="text-center p-8 bg-white shadow-2xl rounded-xl border border-red-200">
					<XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
					<h2 className="text-3xl font-bold text-gray-800 mb-2">
						Unsubscribe Failed
					</h2>
					<p className="text-lg text-gray-600">
						You are currently not subscribed to our Newsletter.
					</p>
					<p className="mt-4 text-sm text-gray-500">
						Error code: {newsletterHash}
					</p>
				</div>
			</Layout>
		);
	}

	// --- Main Unsubscribe Form/Confirmation ---

	return (
		<Layout>
			<div className="bg-white p-8 sm:p-12 shadow-2xl rounded-2xl w-full max-w-lg transition-all duration-300">
				<div className="text-center mb-8">
					<Mail className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
					<h2 className="text-3xl font-extrabold text-gray-900">
						Sad to See You Go
					</h2>
					<p className="mt-2 text-lg text-gray-600">
						We confirm your request to unsubscribe.
					</p>
				</div>

				{/* Reason Selection */}
				<h3 className="text-xl font-semibold mb-4 text-gray-800 border-b pb-2">
					Optional: Tell us why you&apos;re leaving
				</h3>
				<div className="space-y-3">
					{REASONS.map((reason) => (
						<label
							key={reason}
							className="flex items-center space-x-3 cursor-pointer p-3 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors duration-150"
						>
							<input
								type="radio"
								name="reason"
								value={reason}
								checked={selectedReason === reason}
								onChange={() => {
									setSelectedReason(reason);
									if (reason !== 'Other (please specify)') {
										setOtherReasonText('');
									}
								}}
								className="text-indigo-600 focus:ring-indigo-500 h-4 w-4 border-gray-300"
							/>
							<span className="text-sm font-medium text-gray-700">
								{reason}
							</span>
						</label>
					))}
				</div>

				{/* Other Reason Textarea */}
				{selectedReason === 'Other (please specify)' && (
					<div className="mt-4">
						<textarea
							value={otherReasonText}
							onChange={(e) => setOtherReasonText(e.target.value)}
							rows={3}
							placeholder="Please elaborate on why you are leaving..."
							className="text-indigo-600 mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-3"
						/>
					</div>
				)}

				{/* Confirmation Button */}
				<button
					onClick={() => setIsConfirming(true)}
					className="w-full mt-8 flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-md text-base font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 transition-colors duration-200"
					disabled={isLoading}
				>
					{isLoading ? (
						<Loader2 className="w-5 h-5 animate-spin mr-2" />
					) : (
						'Confirm Unsubscribe'
					)}
				</button>
				{/* <p className="mt-4 text-xs text-gray-400 text-center">
					Hash: {newsletterHash.substring(0, 10)}...
					{newsletterHash.substring(newsletterHash.length - 10)}
				</p> */}
			</div>

			{/* Confirmation Modal */}
			{isConfirming && (
				<ConfirmationModal
					onConfirm={handleUnsubscribe}
					onCancel={() => setIsConfirming(false)}
					isLoading={isLoading}
				/>
			)}
		</Layout>
	);
};

export default UnsubscribeForm;

// --- Helper Components ---

// layout wrapper for centering content
const Layout = ({ children }: LayoutProps) => (
	<div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
		{children}
	</div>
);

// Confirmation Modal Component
const ConfirmationModal = ({
	onConfirm,
	onCancel,
	isLoading,
}: ConfirmationModalProps) => (
	<div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50">
		<div className="bg-white rounded-xl shadow-3xl p-8 max-w-md w-full animate-in zoom-in-50">
			<div className="text-center">
				<HeartHandshake className="w-10 h-10 text-red-500 mx-auto mb-4" />
				<h3 className="text-2xl font-bold text-gray-900">
					Are you absolutely sure?
				</h3>
				<div className="mt-4 text-gray-600">
					<p>
						You are about to stop receiving updates from us. You&apos;ll miss
						out on our best content!
					</p>
				</div>
			</div>
			<div className="mt-6 flex justify-between space-x-3">
				<button
					onClick={onCancel}
					type="button"
					className="flex-1 inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:mt-0 sm:text-sm"
				>
					Cancel
				</button>
				<button
					onClick={onConfirm}
					type="button"
					className="flex-1 inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:text-sm disabled:opacity-50"
					disabled={isLoading}
				>
					{isLoading ? (
						<Loader2 className="w-5 h-5 animate-spin mr-2" />
					) : (
						'Yes, Unsubscribe'
					)}
				</button>
			</div>
		</div>
	</div>
);
