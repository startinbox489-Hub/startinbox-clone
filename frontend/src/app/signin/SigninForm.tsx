'use client';

import React, { use, useCallback, useEffect, useState } from 'react';
import { X } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { signIn as NextSignin, useSession } from 'next-auth/react';
import { isEmail } from 'class-validator';

import { UserModel } from '@/types/users.types';
import { PaymentUtil } from '@/app/checkout/util';
import { useAuthStore } from '@/store/authStore';
import { track } from '@/lib/client/metaPixel';
import { useAuth } from '@/context/AuthProvider';

const SigninForm: React.FC<{
	searchParams: Promise<{ plan?: string; next?: string }>;
}> = ({ searchParams }) => {
	const { data: googleOauth2Session } = useSession();
	const { signIn } = useAuth();
	const router = useRouter();
	const [signupEmail, setSignupEmail] = useState<string>('');

	const saveUserToState = useAuthStore((s) => s.signin);

	const params = use(searchParams);
	const [nextPage, setNextPage] = useState<string | undefined>(params.next);

	const selectedPlan = params.plan;

	useEffect(() => {
		if (selectedPlan && ['0', '1', '2', '3'].includes(selectedPlan)) {
			localStorage.setItem(
				'tempIdea',
				JSON.stringify({
					tempIdea: '',
					planIdx: Number(selectedPlan),
					selectedAddOns: [],
				}),
			);
		}
	}, [selectedPlan]);

	const [formData, setFormData] = useState({
		email: signupEmail,
		password: '',
	});
	const [isSubmitting, setIsSubmitting] = useState(false);

	const [error, setError] = useState<null | string>(null);
	const [passwordVisible, setPasswordVisible] = useState(false);
	const [buttonMessage, setButtonMessage] = useState('Sign In');

	const closeModal = useCallback(() => setError(null), []);

	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: value,
		}));
	};

	const validatePassword = useCallback((password: string): boolean | string => {
		if (!password) return '';

		const hasUppercase = /[A-Z]/.test(password);
		const hasLowercase = /[a-z]/.test(password);
		const hasDigit = /\d/.test(password);
		const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(
			password,
		);
		const isLongEnough = password.length >= 8;

		if (!hasUppercase) return false;
		if (!hasLowercase) return false;
		if (!hasDigit) return false;
		if (!hasSpecialChar) return false;
		if (!isLongEnough) return false;
		return '';
	}, []);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!isEmail(formData.email) || formData.password.trim().length < 8) {
			return;
		}
		setIsSubmitting(true);
		setButtonMessage('Signing In...');
		setError(null);
		const isValidPassword = validatePassword(formData.password);
		if (typeof isValidPassword === 'boolean') {
			setError('Invalid Credentials');
			setIsSubmitting(false);
			setButtonMessage('Signin');
			return;
		}

		try {
			const response = await fetch('/api/v1/auth/signin', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(formData),
				credentials: 'include',
			});

			if (response.ok) {
				let nextPage_ = '/';
				if (nextPage) {
					nextPage_ = nextPage?.startsWith('/') ? nextPage : `/${nextPage}`;
				}
				const data = await response.json();
				localStorage.setItem('userData', JSON.stringify(data.user));
				signIn(data.user);
				PaymentUtil.saveToLocalStorage('userData', data.user);
				router.refresh(); // Trigger a full page refresh to re-render Server Components
				const pendingTransaction = PaymentUtil.getFromLocalStorage(
					'pending_transaction',
				);
				localStorage.removeItem('signupEmail');
				setSignupEmail('');
				const event_id = track('Login', { method: 'email' });
				if (nextPage) {
					router.push(nextPage_);
					return;
				}

				if (pendingTransaction) {
					router.push('/checkout');
					return;
				}

				saveUserToState(data.user);
				router.push('/');
				return;
			} else if ([400, 401, 403, 402, 429, 422].includes(response.status)) {
				const data = await response.json();
				setError(
					data.message || 'Sign-in failed. Please check your credentials.',
				);
				setIsSubmitting(false);
				setButtonMessage('Signin');
			} else {
				setError('Internal Server Error. Sign-in failed.');
				setIsSubmitting(false);
				setButtonMessage('Signin');
			}
		} catch (err) {
			setError('An error occurred. Please try again later.');
			console.error('error: ', err);
		} finally {
			setIsSubmitting(false);
			setButtonMessage('Signin');
		}
	};

	useEffect(() => {
		if (!googleOauth2Session) return;
		if (!googleOauth2Session?.idToken || googleOauth2Session?.idToken === '')
			return;

		const signinWithGoogle = async () => {
			try {
				const res = await fetch('/api/v1/auth/signingoogle', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						id_token: googleOauth2Session.idToken,
						agreed_to_terms: true,
					}),
					credentials: 'include',
				});
				const data = await res.json();
				// handle errors
				if (![201, 200].includes(res.status)) {
					if (
						res.status === 404 &&
						data.message.startsWith(
							'No account found for this email. Please sign up',
						)
					) {
						setError(
							'No account found for this email. Kindly signup if you are yet to do so.',
						);
						return;
					}
					setError('Google Signin failed.');
					console.log('Google signin: ', data.message);
					return;
				}
				const userModel = data.user as UserModel;
				if (!userModel) {
					setError('Google Signin failed!');
					return;
				}
				signIn(userModel);
				saveUserToState(userModel);
				localStorage.setItem('userData', JSON.stringify(data.user));
				router.refresh();
				const pendingTransaction =
					PaymentUtil.getFromLocalStorage('pendingTransaction');
				localStorage.removeItem('signupEmail');
				setSignupEmail('');
				const event_id = track('Login', { method: 'google' });
				let nextPage_ = '/';
				if (nextPage) {
					nextPage_ = nextPage?.startsWith('/') ? nextPage : `/${nextPage}`;
				}
				if (pendingTransaction) {
					router.push(nextPage_);
					return;
				}
				if (nextPage_) {
					router.push(nextPage_);
					return;
				}
				router.push('/');
			} catch (e) {
				console.error('error signing up user: ', e);
			}
		};

		if (googleOauth2Session.idToken.length > 0) signinWithGoogle();
	}, [googleOauth2Session, nextPage, router, saveUserToState, signIn]);

	useEffect(() => {
		const userData = localStorage.getItem('userData');
		if (userData) {
			let nextPage_ = '/';
			if (nextPage) {
				nextPage_ = nextPage?.startsWith('/') ? nextPage : `/${nextPage}`;
			}
			if (nextPage_) {
				router.push(nextPage_);
				return;
			}
			router.push('/');
			return;
		}
		const signupEmailExists = localStorage.getItem('signupEmail');
		if (signupEmailExists) {
			setSignupEmail(signupEmailExists);
		}
	}, [nextPage, params.next, router, signupEmail]);

	return (
		<div className="bg-white p-8 rounded-lg shadow-lg w-250 mx-auto my-10 sm:w-250">
			<div className="flex justify-center mb-6">
				<Image
					src="/logo-svg-1.svg"
					alt="StartInBox Logo"
					width={180}
					height={90}
					// style={{ width: 'auto', height: 'auto' }}
				/>
			</div>
			<h2 className="text-center text-2xl font-bold text-gray-900 mb-6">
				Sign In to continue using StartInBox services
			</h2>

			{/* Google Sign-in Button */}
			<button
				className="w-full flex items-center justify-center border border-gray-300 rounded-lg py-3 px-4 mb-4 font-semibold text-gray-700 hover:bg-gray-50 transition"
				onClick={() =>
					NextSignin('google', {
						callbackUrl: `/signin`,
					})
				}
			>
				<Image
					src="/social-icon.svg"
					alt="Google"
					width={20}
					height={20}
					className="mr-2"
				/>
				Sign In with Google
			</button>
			<div className="text-center text-gray-500 mb-4">Or</div>

			<form onSubmit={handleSubmit} className="space-y-4">
				<div>
					<label
						htmlFor="email"
						className="block text-sm font-medium text-gray-700"
					>
						Email
					</label>
					<input
						type="email"
						id="email"
						name="email"
						placeholder="Enter registered email"
						value={formData.email}
						onChange={handleChange}
						required
						className="mt-1 block w-full border-gray-300 rounded-md shadow-sm p-3 focus:ring-purple-500 focus:border-purple-500 text-gray-700"
					/>
				</div>

				<div>
					<label
						htmlFor="password"
						className="block text-sm font-medium text-gray-700"
					>
						Password
					</label>
					<div className="relative mt-1">
						<input
							type={passwordVisible ? 'text' : 'password'}
							id="password"
							name="password"
							placeholder="Enter Password"
							value={formData.password}
							onChange={handleChange}
							required
							className="block w-full border-gray-300 rounded-md shadow-sm p-3 focus:ring-purple-500 focus:border-purple-500 text-gray-700"
						/>
						<span
							className="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer"
							onClick={() => setPasswordVisible(!passwordVisible)}
						>
							<svg
								className="h-5 w-5 text-gray-400"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d={
										passwordVisible
											? 'M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.988 9.988 0 013.91-4.704M15 12a3 3 0 11-6 0 3 3 0 016 0z'
											: 'M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.086 7.523 4 12 4s8.268 3.086 9.542 8c-1.274 4.914-5.065 8-9.542 8s-8.268-3.086-9.542-8z'
									}
								/>
							</svg>
						</span>
					</div>
				</div>

				<button
					type="submit"
					disabled={isSubmitting}
					className="w-full py-3 rounded-lg text-white font-semibold text-lg transition-transform transform hover:scale-105"
					style={{
						background: 'linear-gradient(to right, #6D28D9, #A78BFA)',
					}}
				>
					{buttonMessage}
				</button>
			</form>

			<div className="mt-6 text-center text-gray-600">
				Don&apos;t have an account?{' '}
				<Link href="/signup" className="text-purple-600 hover:text-purple-500">
					Sign Up
				</Link>
			</div>

			{/* Custom Modal for Errors */}
			{error && (
				<div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
					<div className="bg-white p-6 rounded-lg shadow-2xl w-full max-w-sm text-center">
						<div className="flex justify-end">
							<button
								onClick={closeModal}
								className="text-gray-400 hover:text-gray-700"
							>
								<X className="h-5 w-5" />
							</button>
						</div>
						<h3 className="text-xl font-bold text-red-600 mb-4 mt-2">Error</h3>
						<p className="text-gray-700 mb-6">{error}</p>
						<button
							onClick={closeModal}
							className="bg-red-500 hover:bg-red-600 text-white font-semibold py-2 px-4 rounded-lg transition"
						>
							Close
						</button>
					</div>
				</div>
			)}
		</div>
	);
};

export default SigninForm;
