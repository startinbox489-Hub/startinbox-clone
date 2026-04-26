'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { IdeaModelI, TempIdeaI, ValidateIdeaSectionProps } from './interface';
import { useRouter } from 'next/navigation';
import { ApiInitiatePayResponseI } from '@/types/paymentVerification.types';
import Image from 'next/image';
import { UserModel } from '@/types/users.types';

import { track } from '@/lib/client/metaPixel';
import { ChevronDownIcon } from 'lucide-react';
import LoginAlertCard from '@/components/client/LoginAlert';
import { IUserActivePlan } from '@/components/client/Header/interface';

const spinnerStyle = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.animate-spin-custom {
  animation: spin 1s linear infinite;
}
`;

const WARNINGTHRESHOLD = 80;

const ValidateIdeaSection = ({ plans, addOns }: ValidateIdeaSectionProps) => {
	const [user, setUser] = useState<UserModel | null>(null);
	const [showLoginAlert, setShowLoginAlert] = useState<boolean>(false);
	const ModalWrapper = (
		<div className="fixed inset-0 z-50 bg-opacity-50 backdrop-blur-sm">
			<LoginAlertCard onClose={() => setShowLoginAlert(false)} />
		</div>
	);
	const router = useRouter();

	const [tempIdea, setTempIdea] = useState<TempIdeaI | null>(null);

	const [idea, setIdea] = useState(tempIdea?.tempIdea || '');
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [isConsulting, setIsConsulting] = useState(false);
	const [wantsPm, setWantsPm] = useState(false);
	const [isSubmittingToPay, setIsSubmittingToPay] = useState(false);
	const [error, setError] = useState('');
	const [agreedToTerms, setAgreedToTerms] = useState(false);
	const [quantity, setQuantity] = useState(0);
	const [showCharCount, setShowCharCount] = useState<boolean>(false);

	const percentage = useMemo(() => {
		return Math.round((idea.length / 4_000) * 100);
	}, [idea.length]);

	const isNearLimit = useMemo(() => {
		return percentage >= WARNINGTHRESHOLD;
	}, [percentage]);

	const isOverLimit = useMemo(() => {
		return idea.length > 4_000;
	}, [idea.length]);

	const [selectedAddOns, setSelectedAddOns] = useState<
		{ id: string; amount: number; unit: string }[]
	>(tempIdea?.selectedAddOns || []); // startup-consultant
	const [showConditionsModal, setShowConditionsModal] = useState(false);

	const [selectedPlanIdx, setSelectedPlanIdx] = useState(
		tempIdea?.planIdx || 0,
	);

	const selectedPlan = plans.find((p) => p.idx === selectedPlanIdx);
	const consultSelected =
		selectedAddOns.find((a) => a.id === 'startup-consultant') !== undefined;
	const pmSelected =
		selectedAddOns.find((a) => a.id === 'product-manager') !== undefined;

	useEffect(() => {
		if (consultSelected) setIsConsulting(consultSelected);
	}, [consultSelected]);
	useEffect(() => {
		if (pmSelected) setWantsPm(pmSelected);
	}, [pmSelected]);

	//  HANDLE IDEA CHANGE
	const handleIdeaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		const newValue = e.target.value;
		setIdea(newValue);
		if (newValue.trim() !== '') {
			setShowCharCount(true);
		} else {
			setShowCharCount(false);
		}

		if (newValue === '') {
			setError('');
			return;
		} else {
			setError('');
		}
	};

	//  CALCULATE TOTAL
	const calculateTotal = () => {
		let total = selectedPlan?.price ? selectedPlan.price : 0;
		selectedAddOns.forEach((addOn) => {
			total = addOn.amount + Number(total);
		});
		return total;
	};

	//  HANDLE ADD ON CHANGE
	const handleAddOnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { id, checked } = e.target;

		if (checked) {
			const addOn = addOns.find((a) => a.id === id);
			if (addOn) {
				setSelectedAddOns((prev) => [
					...prev,
					{
						id: addOn.id,
						amount: addOn.prices[0].amount,
						unit: addOn.prices[0].unit,
					},
				]);
			}
		} else {
			setSelectedAddOns((prev) => prev.filter((item) => item.id !== id));
		}
	};

	//  HANDLE ADD ON PRICE CHANGE

	const handleAddOnPriceChange = (addOnId: string, priceIndex: number) => {
		const addOn = addOns.find((a) => a.id === addOnId);
		if (addOn) {
			const newAddOns = selectedAddOns.map((item) => {
				if (item.id === addOnId) {
					return { ...item, amount: addOn.prices[priceIndex].amount };
				}
				return item;
			});
			setSelectedAddOns(newAddOns);
		}
	};

	//  HANDLE IDESUBMIT
	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		if (idea.trim().length < 10) {
			setError('Startup Idea is too short');
			return;
		} else if (idea.trim().length > 4000) {
			setError('Startup Idea cannot be more than 4,000');
			return;
		} else {
			setError('');
		}

		if (!user || user === null) {
			localStorage.setItem(
				'tempIdea',
				JSON.stringify({
					tempIdea: idea,
					planIdx: selectedPlanIdx,
					selectedAddOns,
				}),
			);

			localStorage.setItem(
				'selectedAddOns',
				JSON.stringify({
					selectedAddOns,
				}),
			);
			setShowLoginAlert(true);
			return;
		}

		if (selectedPlanIdx > 0 || selectedAddOns.length > 0) {
			let qty = selectedAddOns.length;
			if (selectedPlanIdx > 0) qty += 1;
			setQuantity(qty);
		}
		setIsSubmitting(true);

		localStorage.setItem(
			'IsConsulting',
			JSON.stringify({
				isConsulting,
			}),
		);
		// console.log('validate isConsulting: ', isConsulting);

		if (!user || user === null) {
			localStorage.setItem(
				'tempIdea',
				JSON.stringify({
					tempIdea: idea,
					planIdx: selectedPlanIdx,
					selectedAddOns,
				}),
			);

			localStorage.setItem(
				'selectedAddOns',
				JSON.stringify({
					selectedAddOns,
				}),
			);
			router.push('/signin');
			return;
		}

		setShowConditionsModal(true);
	};

	//  HANDLE PROCEED TO PAY
	const handleProceedToPay = async () => {
		setIsSubmittingToPay(true);
		localStorage.setItem(
			'tempIdea',
			JSON.stringify({
				tempIdea: idea,
				planIdx: selectedPlanIdx,
				selectedAddOns,
			}),
		);
		if (!user || user === null) {
			router.push('/signin');
			return;
		}
		if (selectedPlanIdx === 0 && selectedAddOns.length < 1) {
			// go straight to idea validation without payment
			const selectedPlan = plans.find((p) => p.idx === selectedPlanIdx);
			// validate user idea prompt.
			await handleValidateIdea(selectedPlan?.idx || 0, idea);
			return;
		}

		await sendIdeaToBackend(idea, selectedPlanIdx, selectedAddOns);
	};

	//  HANDLE CANCEL PAY
	const handleCancelConditions = () => {
		setShowConditionsModal(false);
		setIsSubmitting(false);
	};

	//  HANDLE INITIATE PAYMENT
	const sendIdeaToBackend = async (
		prompt: string,
		planIdx: number,
		addOns: { unit: string; amount: number; id: string }[],
	) => {
		// console.log('req payload addOns: ', addOns);
		try {
			const selectedPlanData = plans.find((plan) => {
				return plan.idx === planIdx;
			});

			// for META PIXEL
			const cart: Record<string, string | number>[] = [];
			if (wantsPm) {
				const pm = selectedAddOns.find((a) => a.id === 'product-manager');
				cart.push({
					id: 'product_manager',
					item_price: pm ? pm.amount : 0,
					quantity: 1,
				});
			}

			// for META PIXEL
			if (isConsulting) {
				const expertConsult = selectedAddOns.find(
					(a) => a.id === 'startup-consultant',
				);
				cart.push({
					id: 'expert_consultation',
					item_price: expertConsult ? expertConsult.amount : 0,
					quantity: 1,
				});
			}

			// for META PIXEL
			if (selectedPlan?.id) {
				cart.push({
					id: `subscription_plan:${selectedPlan?.id}`,
					item_price: selectedPlan ? selectedPlan.id : 0,
					quantity: 1,
				});
			}

			const purchase_event_id = track('InitiateCheckout', {
				value: calculateTotal(),
				currency: 'USD',
				contents: cart,
			}) as string;

			// proceed to generate payment link
			const initPayResponse = await fetch('/api/v1/payments', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					subscription_plan_id: selectedPlanData?.id,
					...(addOns.length > 0 && { adds_on_service_ids: addOns }),
					purchase_event_id,
					subscription_plan_idx: selectedPlanData?.idx,
					idx: selectedPlanData?.idx,
				}),
				credentials: 'include',
			});
			const data: ApiInitiatePayResponseI = await initPayResponse.json();
			// console.log('init pay data: ', data);

			if (initPayResponse.status === 401) {
				localStorage.removeItem('userData');
				router.push('/signin');
				return;
			}
			if (initPayResponse.status === 409) {
				setIsSubmittingToPay(false);
				return;
			}

			if (data.message.startsWith('Invalid amount or unit for adds-on')) {
				// console.log(data.message);
				return;
			}
			// check for unused payment
			if (
				data.message.startsWith('Unused active payment detected') &&
				data?.data?.has_active_payment
			) {
				// validate user idea prompt.
				await handleValidateIdea(selectedPlanData?.idx || 0, prompt);
				return;
			}
			const payment_link = data?.data?.payment_link;
			if (payment_link && payment_link !== '') {
				// redirect to payment provider checkout
				window.location.href = payment_link; // handled by /checkout path
				return;
			}
		} catch (error) {
			console.error('error validating idea: ', error);
		}
	};

	//  HANDLE VALIDATE IDEA
	const handleValidateIdea = async (idx: number, prompt: string) => {
		const userActivePlans = localStorage.getItem('si_user_plans');
		const parsedUserActivePlans = userActivePlans
			? (JSON.parse(userActivePlans) as IUserActivePlan[])
			: undefined;
		let type_ = 'oneoff';
		parsedUserActivePlans?.forEach((p) => {
			if (p.type === 'reoccurring' && p.remaining_credits > 0) {
				type_ = 'reoccurring';
			}
		});
		try {
			const response = await fetch('/api/v1/validateidea', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					prompt,
					plan_id: idx,
					idx,
					type_: idx > 0 ? 'oneoff' : type_,
				}),
				credentials: 'include',
			});

			const data = await response.json();

			if (response.ok) {
				const ideaReply: IdeaModelI = data?.idea;
				localStorage.setItem(
					'ideaReply',
					JSON.stringify({
						preview: ideaReply.idea_validation,
						ideaScore: ideaReply.idea_score,
						prompt: idea,
						id: ideaReply.id,
						sentReview: false,
						idx: data.idx,
						canceledPay: false,
					}),
				);
				localStorage.setItem(
					'ideaReplyPlanId',
					JSON.stringify({
						PlanIdx: data.idx,
					}),
				);
				localStorage.removeItem('IsConsulted');
				// localStorage.removeItem('IsConsulting');
				router.refresh();
				setError('');
				// for META PIXEL
				const event_id = track('Lead', { category: 'idea_validation' });

				const response = await fetch('/api/v1/plans/active', {
					method: 'GET',
					credentials: 'include',
				});
				if (response.ok) {
					const data = (await response.json()).data as IUserActivePlan[];
					localStorage.setItem('si_user_plans', JSON.stringify(data)); // array
				}

				router.push(`/analysis?i=${data?.idx}`);
				setIsSubmitting(false);
				return;
			} else if (response.status > 499) {
				setError('Something went Wrong. Could not complete Idea validation.');
				console.log(
					'Something went Wrong. Could not complete Idea validation.',
				);
				setIsSubmittingToPay(false);
				setShowConditionsModal(false);
				setIsSubmitting(false);
				router.push('/');
				return;
			} else if (response.status === 401) {
				setError('Redirecting to Signin page');
				console.log('Redirecting to Signin page');
				setIsSubmittingToPay(false);
				setShowConditionsModal(false);
				setIsSubmitting(false);
				localStorage.removeItem('userData');
				router.push(`/signin?next=${encodeURIComponent('/')}`);
				return;
			} else if (response.status === 409) {
				setError(data['message']);
				console.log(data['message']);
				setIsSubmittingToPay(false);
				setShowConditionsModal(false);
				setIsSubmitting(false);
				router.push(`/`);
				return;
			} else if (response.status === 417) {
				setError(data['message']);
				console.log(data['message']);
				setIsSubmittingToPay(false);
				setShowConditionsModal(false);
				setIsSubmitting(false);
				return;
			}
			// TODO: handle other cases
		} catch (error) {
			console.error('Idea validation failed: ', error);
			setError('Could not complete Idea Validation. Something went wrong.');
			console.log('Could not complete Idea Validation. Something went wrong.');
			setIsSubmitting(false);
		}
	};

	useEffect(() => {
		const userData = localStorage.getItem('userData');
		if (userData) {
			setUser(JSON.parse(userData) as UserModel);
		}
	}, []);

	useEffect(() => {
		try {
			const tempIdeaExists = localStorage.getItem('tempIdea');
			// console.log('tempIdeaExists: ', tempIdeaExists);
			if (tempIdeaExists) {
				setTempIdea(JSON.parse(tempIdeaExists));
				setIdea(tempIdea?.tempIdea || '');
				setSelectedAddOns(tempIdea?.selectedAddOns || []);
				setSelectedPlanIdx(tempIdea?.planIdx || 0);
			}
		} catch (error) {
			// Handle potential errors if the user blocks cookies/storage
			console.error('Could not access localStorage:', error);
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [tempIdea?.planIdx]);

	return (
		<div className="bg-gray-100 p-6 mt-18">
			<div
				className={`flex flex-col md:flex-row gap-8 ${
					user ? '' : 'max-w-7xl mx-auto'
				}`}
			>
				{/* Main content section */}
				<div
					id="validate-idea-sec"
					className={`bg-white p-8 rounded-lg shadow-md ${
						user ? 'w-full md:w-3/5' : 'w-full'
					}`}
				>
					<div className="mb-6">
						<h2 className="text-xl font-bold text-gray-800">
							Try StartinBox Now
						</h2>
						<p className="text-gray-800">
							Describe your startup idea and get instant validation
						</p>
						{error !== '' && (
							<div className="text-red-500 text-sm mb-4 text-center">
								{error}
							</div>
						)}
					</div>

					<div className="mb-6">
						<textarea
							className={`w-full h-40 p-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 ${
								isOverLimit
									? 'border-red-500'
									: isNearLimit
										? 'border-yellow-500'
										: 'border-gray-300'
							}`}
							placeholder={`Describe your startup idea in details. What problem are you solving? Who is it for?`}
							id="validate-idea"
							onChange={handleIdeaChange}
							value={idea}
							required
							maxLength={4_002}
						/>
						{showCharCount && (
							<div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-0">
								{/* Character Count */}
								<div className="text-sm">
									<span
										className={
											isOverLimit
												? 'text-red-600 font-medium'
												: 'text-green-600'
										}
									>
										{idea.length} / {4_000} characters
									</span>
									{isOverLimit ? (
										<span className="ml-2 text-red-600">
											({idea.length - 4_000} over limit)
										</span>
									) : (
										idea !== '' &&
										idea.length < 10 && (
											<span className="ml-2 text-red-600">Too short</span>
										)
									)}
								</div>

								{/* Progress bar */}
								<div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
									<div
										className={`h-full ${
											isOverLimit
												? 'bg-red-500'
												: isNearLimit
													? 'bg-yellow-500'
													: 'bg-green-500'
										}`}
										style={{ width: `${Math.min(percentage, 100)}%` }}
									/>
								</div>
							</div>
						)}
					</div>

					<div className="mb-6">
						<h3 className="text-lg font-semibold text-gray-700 mb-2">
							Select a plan
						</h3>
						<div className="grid grid-cols-1 md:grid-cols-4 gap-2 border border-gray-300 p-1 rounded-lg">
							{plans.map((plan) => (
								<button
									key={plan.idx}
									type="button"
									onClick={() => setSelectedPlanIdx(plan.idx)}
									className={`flex-1 py-2 px-4 rounded-md transition-colors duration-200 ${
										selectedPlanIdx === plan.idx
											? 'bg-black text-white shadow-lg'
											: 'text-gray-600 bg-gray-200 hover:bg-gray-300'
									}`}
								>
									{plan.name}
								</button>
							))}
						</div>
					</div>

					{selectedPlan && (
						<div className="mb-6 border-b border-gray-200 pb-4">
							<div className="border-3 rounded-md pr-4 pl-4 pt-2">
								<div className="flex justify-between items-center mb-2">
									<h4 className="text-lg font-bold text-gray-800">
										{selectedPlan.name} Plan
									</h4>
									<div className="text-lg font-bold text-gray-800">{`$${selectedPlan.price}`}</div>
								</div>
								<div className="space-y-2 text-sm text-gray-700">
									{selectedPlan.features?.map((feature, index) => (
										<div key={index} className="flex items-center">
											<span className="text-green-500 mr-2">
												<svg
													className="h-4 w-4"
													fill="currentColor"
													viewBox="0 0 20 20"
												>
													<path
														fillRule="evenodd"
														d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
														clipRule="evenodd"
													/>
												</svg>
											</span>
											{feature.name}
										</div>
									))}
								</div>
								<p className="text-blue-500 font-semibold italic text-sm mt-1">
									{(selectedPlan.idx === 0 && 'No credit card required') || ''}
								</p>
							</div>
						</div>
					)}

					{/* ADD ON SERVICES */}
					<div className="mb-6">
						<h3 className="text-lg font-semibold text-gray-700 mb-2">
							Select adds on service (Optional)
						</h3>
						<div className="space-y-4">
							{addOns.map((addOn) => (
								<div
									key={addOn.id}
									className="flex flex-wrap items-center justify-between p-4 rounded-lg border border-gray-300 gap-2"
								>
									<label className="flex items-center space-x-3 cursor-pointer">
										<input
											type="checkbox"
											id={addOn.id}
											checked={selectedAddOns.some(
												(item) => item.id === addOn.id,
											)}
											onChange={handleAddOnChange}
											className="form-checkbox h-5 w-5 text-purple-600 rounded"
											name={addOn.name}
										/>
										<span className="text-gray-900">{addOn.name}</span>
									</label>
									<div className="relative">
										<select
											className="appearance-none bg-white border border-gray-300 rounded-lg py-2 px-4 pr-8 text-sm cursor-pointer focus:outline-none text-gray-700"
											onChange={(e) =>
												handleAddOnPriceChange(
													addOn.id,
													parseInt(e.target.value),
												)
											}
											name={addOn.name}
										>
											{addOn.prices.map((price) => (
												<option
													key={price.selectedPriceIndex}
													value={price.selectedPriceIndex}
												>
													${price.amount} / {price.unit}
												</option>
											))}
										</select>
										<div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
											<ChevronDownIcon className="h-5 w-5 text-gray-400" />
										</div>
									</div>
								</div>
							))}
						</div>
					</div>

					<div className="flex justify-between items-center py-4 border-t border-gray-200 mb-6">
						<span className="text-lg font-bold text-gray-900">
							Total to Pay:
						</span>
						<span className="text-2xl font-bold text-gray-900">
							${calculateTotal()}
						</span>
					</div>
					<style dangerouslySetInnerHTML={{ __html: spinnerStyle }} />
					<button
						className={`
                    w-full py-3 px-6 rounded-lg font-semibold shadow-lg transition duration-200
                    flex items-center justify-center space-x-2
                    ${
											isSubmittingToPay
												? 'bg-indigo-400 text-indigo-50 cursor-not-allowed'
												: 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-500/50'
										}
                `}
						style={{
							background: 'linear-gradient(to right, #6D28D9, #A78BFA)',
						}}
						onClick={handleSubmit}
						disabled={isSubmitting}
					>
						{isSubmitting
							? (user && (
									<>
										{/* SVG for the rotating loading icon */}
										<svg
											className="w-5 h-5 text-white animate-spin-custom"
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
										<span>{'Validating'}</span>
									</>
								)) ||
								'Redirecting to signin...'
							: 'Validate My Idea'}
					</button>
				</div>

				{/* How It Works & Sample Ideas Section - Renders only when user is logged in */}
				{user && (
					<div className="flex flex-col space-y-8 w-full md:w-2/5">
						{/* How It Works */}
						<div className="p-25 rounded-xl shadow-lg bg-white">
							<h3 className="text-xl font-bold text-gray-900 mb-4">
								How It Works
							</h3>
							<ol className="space-y-6 text-gray-700">
								<li className="flex items-start pt-15">
									<span className="flex-shrink-0 w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold mr-3">
										1
									</span>
									<div>
										<h4 className="font-semibold">Submit Your Idea</h4>
										<p className="text-sm">
											Fill in our quick form with your startup idea — no tech
											jargon needed.
										</p>
									</div>
								</li>
								<li className="flex items-start pt-15">
									<span className="flex-shrink-0 w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold mr-3">
										2
									</span>
									<div>
										<h4 className="font-semibold">AI Validates & Plans</h4>
										<p className="text-sm">
											Our AI analyzes your idea based on market potential,
											problem-solution fit, and business viability.
										</p>
									</div>
								</li>
								<li className="flex items-start pt-15">
									<span className="flex-shrink-0 w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold mr-3">
										3
									</span>
									<div>
										<h4 className="font-semibold">Get Results</h4>
										<p className="text-sm">
											Receive everything neatly packaged via email or WhatsApp
											in under 5 minutes.
										</p>
									</div>
								</li>
							</ol>
						</div>

						{/* Sample Ideas */}
						<div className="p-8 rounded-xl shadow-lg bg-white">
							<h3 className="text-xl font-bold text-gray-900 mb-4">
								Sample Ideas
							</h3>
							<ul className="space-y-4 text-gray-700">
								<li className="pt-15">
									&quot;A mobile app that helps people find and book local
									fitness classes on demand&quot;
								</li>
								<li className="pt-15">
									&quot;A subscription service that delivers curated ingredients
									for cocktails&quot;
								</li>
								<li className="pt-15">
									&quot;An AI-powered platform that helps students improve their
									writing skills&quot;
								</li>
							</ul>
						</div>
					</div>
				)}

				{/* Login ALert Card */}
				{showLoginAlert && ModalWrapper}

				{/* Payment Summary Modal */}
				{showConditionsModal && (
					<div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
						<div className="bg-white p-8 rounded-lg shadow-xl max-w-sm w-full mx-auto text-center">
							<h3 className="text-lg font-bold text-gray-900 mb-6">
								Payment Summary
							</h3>
							{error !== '' && (
								<div className="text-red-500 text-sm mb-4 text-center">
									{error}
								</div>
							)}
							<div className="flex items-center justify-between mb-4 border-b border-gray-200 pb-4">
								<div className="flex items-center space-x-2">
									<Image
										src="/logo-svg-1.svg"
										alt="StartInBox Logo"
										width={24}
										height={24}
									/>
									<span className="font-semibold text-lg text-gray-800">
										StartInBox
									</span>
								</div>
								<span className="text-sm font-semibold text-gray-500">
									Qty: {quantity}
								</span>
							</div>

							<div className="space-y-4 text-left border-b border-gray-200 pb-4 mb-4">
								<div className="flex justify-between items-center text-sm font-medium">
									<span className="text-gray-700">{selectedPlan?.name}</span>
									<span className="text-gray-900">${selectedPlan?.price}</span>
								</div>
								{selectedAddOns.map((addOn) => (
									<div
										key={addOn.id}
										className="flex justify-between items-center text-sm font-medium"
									>
										<span className="text-gray-700">
											{addOns.find((a) => a.id === addOn.id)?.name}
										</span>
										<span className="text-gray-900">${addOn.amount}</span>
									</div>
								))}
							</div>

							<div className="flex justify-between items-center mb-6">
								<div className="text-lg font-bold text-gray-900">
									Total
									<p className="text-xs text-gray-500 font-normal">
										Taxes included
									</p>
								</div>
								<span className="text-2xl font-bold text-blue-600">
									${calculateTotal()}
								</span>
							</div>

							<div className="mb-6 flex items-center justify-center">
								<input
									type="checkbox"
									id="agreeTerms"
									checked={agreedToTerms}
									onChange={(e) => setAgreedToTerms(e.target.checked)}
									className="form-checkbox h-5 w-5 text-purple-600 rounded mr-3"
								/>
								<label htmlFor="agreeTerms" className="text-sm text-gray-600">
									By checking this box, you acknowledge and agree to our{' '}
									<a
										href="/privacy-policy"
										className="text-blue-600 hover:underline"
										target="_blank"
									>
										Privacy Policy
									</a>
								</label>
							</div>

							<div className="flex justify-center space-x-4">
								<button
									type="button"
									onClick={handleCancelConditions}
									className="py-2 px-4 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100"
								>
									Cancel
								</button>
								<style dangerouslySetInnerHTML={{ __html: spinnerStyle }} />
								<button
									type="button"
									onClick={handleProceedToPay}
									disabled={!agreedToTerms}
									// className="py-2 px-4 rounded-lg text-white font-semibold transition-transform transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
									className={`
                    w-full py-3 px-6 rounded-lg font-semibold shadow-lg transition duration-200
                    flex items-center justify-center space-x-2
                    ${
											isSubmittingToPay
												? 'bg-indigo-400 text-indigo-50 cursor-not-allowed'
												: 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-500/50'
										}
                `}
									style={{
										background: 'linear-gradient(to right, #6D28D9, #A78BFA)',
									}}
								>
									{user
										? (isSubmittingToPay && (
												<>
													{/* SVG for the rotating loading icon */}
													<svg
														className="w-5 h-5 text-white animate-spin-custom"
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
													<span>{'Processing Transaction'}</span>
												</>
											)) ||
											'Proceed to Secure Payment'
										: (isSubmittingToPay && 'Redirecting to Signin...') ||
											'Proceed to Secure Payment'}
								</button>
							</div>
						</div>
					</div>
				)}
			</div>
		</div>
	);
};

export default ValidateIdeaSection;
