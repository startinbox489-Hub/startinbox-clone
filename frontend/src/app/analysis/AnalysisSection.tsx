'use client';

import React, { useEffect, useState, use } from 'react';
import { useRouter } from 'next/navigation';

import ReviewPopup from '../../components/client/ReviewPopup';
import { ReviewData } from '@/types/reviewPopup.types';
import { IdeaReply, SelectedAddsOnUnit } from '@/types/analysis.types';
import SubscriptionFooterPrompt from './SubscriptionFooterPrompt';
import { useAuth } from '@/context/AuthProvider';

const AnalysisSection: React.FC<{
	searchParams: Promise<{ i?: string; next?: string }>;
}> = ({ searchParams }) => {
	const params = use(searchParams);
	const { user: userData } = useAuth();

	const selectedPlan = params.i;
	const router = useRouter();

	const [showReviewPopup, setShowReviewPopup] = useState(false);
	const [reviewSent, setReviewSent] = useState(false);
	const [selectedAddOns, setSelectedAddOns] = useState<
		SelectedAddsOnUnit[] | []
	>([]);
	const [ideaReply, setIdeaReply] = useState<null | IdeaReply>(null);
	const [isConsulted, setIsConsulted] = useState<null | boolean>(null);
	const [isConsulting, setIsConsulting] = useState<{
		isConsulting: boolean;
	}>({ isConsulting: false });
	const [showSubscribeOption, setShowSubscribeOption] = useState<{
		idx: number;
		canceledPay: boolean;
	} | null>(null);

	let pmSelected: SelectedAddsOnUnit | null | undefined = null;
	if (selectedAddOns?.length > 0) {
		pmSelected = selectedAddOns?.find(
			(a: SelectedAddsOnUnit) => a.id === 'product-manager',
		);
	}

	useEffect(() => {
		try {
			const selectedAddOnsExists = localStorage.getItem('selectedAddOns');
			if (selectedAddOnsExists && JSON.parse(selectedAddOnsExists).length > 0) {
				setSelectedAddOns(JSON.parse(selectedAddOnsExists));
			}

			const ideaReplyExists = localStorage.getItem('ideaReply');
			if (ideaReplyExists && !ideaReply) {
				const parsedIdeaReplyExists = JSON.parse(ideaReplyExists);
				setIdeaReply(parsedIdeaReplyExists);
				setShowSubscribeOption({
					idx: parsedIdeaReplyExists.idx,
					canceledPay: parsedIdeaReplyExists.canceledPay,
				});
			}

			const isConsultedExists = localStorage.getItem('IsConsulted');
			const parsedIsConsulted: null | { isConsulted: boolean } =
				isConsultedExists ? JSON.parse(isConsultedExists) : null;
			// console.log('parsedIsConsulted: ', parsedIsConsulted);
			if (parsedIsConsulted?.isConsulted && isConsulted !== null) {
				setIsConsulted(parsedIsConsulted.isConsulted);
			}
		} catch (error) {
			// Handle potential errors if the user blocks cookies/storage
			console.error('Could not access localStorage:', error);
		}
	}, [ideaReply, isConsulted, selectedAddOns]);

	useEffect(() => {
		const isConsultingExists = localStorage.getItem('IsConsulting');
		if (isConsultingExists !== null) {
			const parsedIsConsulting: {
				isConsulting: boolean;
			} = JSON.parse(isConsultingExists);
			if (parsedIsConsulting.isConsulting !== isConsulting.isConsulting) {
				setIsConsulting(parsedIsConsulting);
			}
		}
		// show review popup if user is not consulting
		if (isConsulting.isConsulting === false) {
			// Show the popup after a brief delay if the user hasn't already sent a review
			if (reviewSent === false && ideaReply?.sentReview === false) {
				const timer = setTimeout(() => {
					setShowReviewPopup(true);
				}, 40_000); // Wait 40 seconds after component renders

				return () => clearTimeout(timer);
			}
		}
	}, [reviewSent, ideaReply?.sentReview, isConsulting]);

	useEffect(() => {
		if (ideaReply) {
			if (ideaReply?.idx) {
				if (ideaReply.idx < 1 && !ideaReply?.canceledPay) {
					// show popup for pay to view rest of analysis and receive validation in email
					return;
				}
				if (ideaReply.idx > 0) {
					ideaReply.canceledPay = true;
					const reply = localStorage.getItem('ideaReply');
					if (reply) {
						localStorage.setItem(
							'ideaReply',
							JSON.stringify({ ...JSON.parse(reply), canceledPay: true }),
						);
					}
					return;
				}
			}
		}
	}, [ideaReply, ideaReply?.canceledPay, ideaReply?.idx]);

	/**
	 * handles click event if user sub covers consultation or not
	 */
	const handleConsultation = async () => {
		// console.log('IsConsulting: ', isConsulting);
		if (isConsulting.isConsulting && isConsulted !== true) {
			router.push('/consult');
			return;
		}
		return;
	};
	/**
	 * handles click event if user sub covers consultation or not
	 */
	const handleProductManager = async () => {
		console.log('IsConsulting: ', isConsulting);
		if (isConsulting.isConsulting) {
			router.push('/next-step');
		}
	};

	/**
	 * Handler for when the review popup closes (either submitted or skipped)
	 * @param submitted
	 */
	const handleReviewClose = (submitted: boolean) => {
		setShowReviewPopup(false);
		if (submitted) {
			setReviewSent(true); // Prevent showing the popup again
			localStorage.setItem(
				'ideaReply',
				JSON.stringify({
					...ideaReply,
					sentReview: true,
				}),
			);
			console.log('Review submitted successfully!');
		} else {
			console.log('Review skipped by user.');
		}
	};

	/**
	 * Sends review to the backend
	 * @param data
	 * @returns
	 */
	const SendReviewToBackend = async (
		data: ReviewData & { idea_id: string },
	): Promise<void> => {
		const response = await fetch('/api/v1/testimonials', {
			method: 'POST',
			body: JSON.stringify({
				...data,
				testimonial: data.feedback === '' ? null : data.feedback,
				feeback: undefined,
			}),
			headers: { 'Content-Type': 'application/json' },
			credentials: 'include',
		});

		const resData = await response.json();
		if (!response.ok) {
			if (response.status === 401) {
				localStorage.removeItem('userData');
				router.push(
					`/signin?next=${encodeURIComponent(`/analysis?i=${selectedPlan}`)}`,
				);
			} else if (response.status === 422) {
				console.log('422 for testimonials: ', resData.message);
			}
		}
		return;
	};

	const handleNavigation = () => {
		router.push('/');
	};
	return (
		<div>
			<div className="bg-white p-8 rounded-xl shadow-lg border border-gray-200 mb-12">
				<h1 className="text-2xl font-extrabold text-gray-900 mb-4">
					{selectedPlan === '0'
						? 'FULL ANALYSIS AND BREAKDOWN OF YOUR IDEA:'
						: 'FULL ANALYSIS AND BREAKDOWN OF YOUR IDEA HAS BEEN SENT:'}
				</h1>
				<p className="text-gray-600">
					Email:{' '}
					<span className="font-semibold text-purple-600">
						{userData?.email || ''}
					</span>
				</p>
				{/* NOTE: Temporary disable Whatsapp */}
				{/* <p className="text-gray-600 mb-6">
					WhatsApp:{' '}
					<span className="font-semibold text-purple-600">
						{userData?.phone_number || ''}
					</span>
				</p> */}

				<div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
					<h2 className="text-lg font-bold text-gray-900 mb-2">
						Startup Idea:
					</h2>
					<p className="text-gray-700 mb-4">{ideaReply?.prompt || ''}</p>
					<h2 className="text-lg font-bold text-gray-900 mb-2">Preview:</h2>
					<p className="text-gray-700 mb-4">{ideaReply?.preview || ''}</p>
					<h2 className="text-lg font-bold text-gray-900">
						Idea Score:{' '}
						<span className="font-semibold">
							{ideaReply?.ideaScore ? `${ideaReply?.ideaScore} / 100` : 'N/A'}
						</span>
					</h2>
				</div>

				<div className="mt-6 flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
					<button
						className="flex-1 py-3 px-6 rounded-lg border border-gray-300 bg-white text-gray-800 font-semibold hover:bg-gray-100 transition-colors"
						onClick={handleConsultation}
					>
						{isConsulted === true
							? 'Consultation Scheduled'
							: 'Consult with a Startup Expert'}
					</button>
					<button
						className="flex-1 py-3 px-6 rounded-lg border border-gray-300 bg-white text-gray-800 font-semibold hover:bg-gray-100 transition-colors"
						onClick={handleProductManager}
					>
						{pmSelected
							? `Product Manager Hired: $${pmSelected.amount} / ${pmSelected.unit}`
							: 'Plan the Next Steps with Product Manager'}
					</button>
				</div>
			</div>

			<div className="flex justify-center mb-12">
				<button
					className="py-4 px-12 rounded-lg text-white font-semibold text-lg transition-transform transform hover:scale-105"
					style={{ background: 'linear-gradient(to right, #6D28D9, #A78BFA)' }}
					onClick={handleNavigation}
				>
					New Validation
				</button>
			</div>

			{/* Render the Review Popup. render if user is not consulting */}
			{ideaReply?.id && (
				<ReviewPopup
					isOpen={showReviewPopup}
					idea_id={ideaReply.id}
					onClose={handleReviewClose}
					sendReviewToBackend={SendReviewToBackend}
				/>
			)}

			{showSubscribeOption?.idx === 0 && !showSubscribeOption.canceledPay && (
				<SubscriptionFooterPrompt />
			)}
		</div>
	);
};

export default AnalysisSection;
