'use client';

import React, { useCallback, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { signIn, useSession } from 'next-auth/react';
import { useEffect } from 'react';

import { UserModel } from '@/types/users.types';
import AuthServiceClient from '@/lib/client/authService';
import RegistrationSuccessPopup from './RegistrationSuccessPopup';
import { CountryCodeDropdown } from './CountryCodeSelect';
import { track } from '@/lib/client/metaPixel';
import { ValidationErrors } from '@/types/signup.types';

const SignupForm = () => {
	const router = useRouter();
	const { data: googleOauth2Session } = useSession();

	const [showSuccessPopup, setShowSuccessPopup] = useState(false);
	const [registeredUserName, setRegisteredUserName] = useState('');
	const [homePageName, setHomePageName] = useState('Home Page');
	const [homePagePath, setHomePagePath] = useState('/');
	const [buttonMessage, setButtonMessage] = useState('Sign Up');

	// form state
	const [formData, setFormData] = useState({
		email: '',
		countryCode: '+1',
		contactNumber: '',
		password: '',
		confirmPassword: '',
		agreedToTerms: false,
	});
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [error, setError] = useState('');
	const [passwordVisible, setPasswordVisible] = useState(false);
	const [confirmPasswordVisible, setConfirmPasswordVisible] = useState(false);
	const [validationErrors, setValidationErrors] = useState<ValidationErrors>(
		{},
	);
	const [passwordStrength, setPasswordStrength] = useState(0);

	const validateEmail = useCallback((email: string) => {
		if (!email) return '';
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailRegex.test(email)) return 'Please enter a valid email address';
		return '';
	}, []);

	const validatePassword = useCallback((password: string) => {
		if (!password) return '';

		const hasUppercase = /[A-Z]/.test(password);
		const hasLowercase = /[a-z]/.test(password);
		const hasDigit = /\d/.test(password);
		const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(
			password,
		);
		const isLongEnough = password.length >= 8;

		const errors: string[] = [];
		if (!hasUppercase) errors.push('uppercase letter');
		if (!hasLowercase) errors.push('lowercase letter');
		if (!hasDigit) errors.push('digit');
		if (!hasSpecialChar) errors.push('special character');
		if (!isLongEnough) errors.push('at least 8 characters');

		// Calculate strength (0-100)
		let strength = 0;
		if (hasUppercase) strength += 20;
		if (hasLowercase) strength += 20;
		if (hasDigit) strength += 20;
		if (hasSpecialChar) strength += 20;
		if (isLongEnough) strength += 20;
		setPasswordStrength(strength);

		if (errors.length > 0) {
			return `Password must contain: ${errors.join(', ')}`;
		}
		return '';
	}, []);

	const validateContactNumber = useCallback(
		(number: string, countryCode: string) => {
			if (!number) return '';

			// Remove non-digits
			const cleanNumber = number.replace(/\D/g, '');

			if (cleanNumber.length < 7) return 'Phone number seems too short';
			if (cleanNumber.length > 15) return 'Phone number seems too long';

			// Validate based on country code
			if (countryCode === '+1' && cleanNumber.length !== 10) {
				return 'US/Canada numbers must be 10 digits';
			}
			if (countryCode === '+234' && cleanNumber.length !== 10) {
				return 'Nigerian numbers must be 10 digits';
			}

			return '';
		},
		[],
	);

	const validateConfirmPassword = useCallback(
		(confirm: string, password: string) => {
			if (!confirm) return '';
			if (confirm !== password) return 'Passwords do not match';
			return '';
		},
		[],
	);

	// Real-time validation on input change
	useEffect(() => {
		const errors: ValidationErrors = {};

		const emailError = validateEmail(formData.email);
		if (emailError) errors.email = emailError;

		const passwordError = validatePassword(formData.password);
		if (passwordError) errors.password = passwordError;

		const contactError = validateContactNumber(
			formData.contactNumber,
			formData.countryCode,
		);
		if (contactError) errors.contactNumber = contactError;

		const confirmError = validateConfirmPassword(
			formData.confirmPassword,
			formData.password,
		);
		if (confirmError) errors.confirmPassword = confirmError;

		setValidationErrors(errors);
	}, [
		formData,
		validateEmail,
		validatePassword,
		validateContactNumber,
		validateConfirmPassword,
	]);

	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value, type, checked } = e.target;
		setFormData((prev) => ({
			...prev,
			[name]: type === 'checkbox' ? checked : value,
		}));
	};

	const handleCountryCodeChange = (newValue: string) => {
		setFormData((prevData) => ({
			...prevData,
			countryCode: newValue,
		}));
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		// blur any focused input (especially password) before submit
		(document.activeElement as HTMLElement)?.blur();
		const isEmailValid = AuthServiceClient.validateEmail(formData.email);

		const errors: ValidationErrors = {};
		errors.email = validateEmail(formData.email);
		errors.password = validatePassword(formData.password);
		errors.contactNumber = validateContactNumber(
			formData.contactNumber,
			formData.countryCode,
		);
		errors.confirmPassword = validateConfirmPassword(
			formData.confirmPassword,
			formData.password,
		);

		setValidationErrors(errors);

		// Check if any errors exist
		const hasErrors = Object.values(errors).some((error) => error);
		if (hasErrors || !formData.agreedToTerms) {
			return;
		}

		const isValidPhoneNumber = AuthServiceClient.validatePhoneNumber(
			formData.contactNumber,
			formData.countryCode,
		);
		if (typeof isValidPhoneNumber === 'string') {
			// console.log('formData.contactNumber: ', formData.contactNumber);
			setError(isValidPhoneNumber);
			return;
		}
		setIsSubmitting(true);
		setButtonMessage('Creating Account...');
		setError('');
		localStorage.setItem('signupEmail', JSON.stringify(formData.email));

		try {
			const response = await fetch('/api/v1/auth/signup', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					...formData,
					phone_number: `${formData.countryCode}${formData.contactNumber}`,
					confirm_password: formData.confirmPassword,
					agreed_to_terms: formData.agreedToTerms,
				}),
			});

			if (response.ok) {
				// Handle successful signup redirect to dashboard
				// console.log('Signup successful!');
				setHomePageName('SIGNIN');
				setHomePagePath('/signin');
				setTimeout(() => {
					setShowSuccessPopup(true);
				}, 400);
				const _ = track('CompleteRegistration', { method: 'email' });
				router.push('/signin');
				return;
			} else {
				const data = await response.json();
				setError(data.message || 'Signup failed. Please try again.');
				setIsSubmitting(false);
				setButtonMessage('Sign Up');
			}
		} catch (err) {
			setError('An error occurred. Please try again later.');
			setShowSuccessPopup(false);
			console.error('error: ', err);
		} finally {
			setIsSubmitting(false);
		}
	};

	useEffect(() => {
		const userData = localStorage.getItem('userData');
		if (userData) {
			setButtonMessage('Redirecting to Home...');
			router.push('/');
			return;
		}
	}, [router]);

	useEffect(() => {
		if (!googleOauth2Session?.idToken) return;

		const signupWithGoogle = async () => {
			try {
				const res = await fetch('/api/v1/auth/signupgoogle', {
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
					setError(data.message);
					return;
				}
				const userModel = data.user as UserModel;
				localStorage.setItem('userData', JSON.stringify(data.user));
				if (userModel.first_name) {
					setRegisteredUserName(userModel.first_name);
				}
				router.refresh();
				setHomePageName('HOME PAGE');
				setHomePagePath('/');
				setShowSuccessPopup(true);
				const _ = track('CompleteRegistration', { method: 'google' });
				router.push('/');
				return;
			} catch (e) {
				setShowSuccessPopup(false);
				console.error('error signing up user: ');
			}
		};

		signupWithGoogle();
	}, [googleOauth2Session, router]);

	// Password strength indicator
	const getPasswordStrengthColor = () => {
		if (passwordStrength < 40) return 'bg-red-500';
		if (passwordStrength < 80) return 'bg-yellow-500';
		return 'bg-green-500';
	};

	return (
		<div className="bg-white pt-8 pb-8 pr-15 pl-15 rounded-lg shadow-lg w-250 mb-20">
			<div className="flex justify-center mb-6">
				<Image
					src="/logo-svg-1.svg"
					alt="StartInBox Logo"
					width={150}
					height={50}
				/>
			</div>
			<h2 className="text-center text-2xl font-bold text-gray-900 mb-6">
				Create your StartInBox account to get started with our services.
			</h2>

			{/* Google Sign-up Button */}
			<button
				className="w-full flex items-center justify-center border border-gray-300 rounded-lg py-3 px-4 mb-4 font-semibold text-gray-700 hover:bg-gray-50 transition"
				onClick={() =>
					signIn('google', {
						callbackUrl: `/signup`,
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
				Sign up with Google
			</button>
			<div className="text-center text-gray-500 mb-4">Or</div>

			{error && (
				<div className="text-red-500 text-sm mb-4 text-center">{error}</div>
			)}

			<form onSubmit={handleSubmit} className="space-y-4">
				{/* Email Field */}
				<div>
					<label
						htmlFor="email"
						className="block text-sm font-medium text-gray-700 mb-1"
					>
						Email
					</label>
					<input
						type="email"
						id="email"
						name="email"
						placeholder="Enter valid email address"
						value={formData.email}
						onChange={handleChange}
						required
						className={`mt-1 block w-full border rounded-md shadow-sm p-3 focus:ring-purple-500 focus:border-purple-500 text-gray-700 ${
							validationErrors.email ? 'border-red-500' : 'border-gray-300'
						}`}
					/>
					{validationErrors.email && (
						<div className="mt-1 text-sm text-red-600 flex items-start gap-1">
							<svg
								className="w-4 h-4 mt-0.5 flex-shrink-0"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fillRule="evenodd"
									d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
									clipRule="evenodd"
								/>
							</svg>
							<span className="break-words flex-1">
								{validationErrors.email}
							</span>
						</div>
					)}
				</div>

				{/* Contact Number Field */}
				<div>
					<label
						htmlFor="contactNumber"
						className="block text-sm font-medium text-gray-700 mb-1"
					>
						Contact Number (WhatsApp)
					</label>
					<div className="mt-1 flex flex-col xs:flex-row gap-2">
						<div className="w-full xs:w-auto">
							<CountryCodeDropdown
								value={formData.countryCode}
								handleOnChange={handleCountryCodeChange}
							/>
						</div>
						<div className="flex-1 min-w-0">
							<input
								type="tel"
								id="contactNumber"
								name="contactNumber"
								placeholder="Enter Your WhatsApp Number"
								value={formData.contactNumber}
								onChange={handleChange}
								className={`block w-full rounded-md border p-3 focus:ring-purple-500 focus:border-purple-500 text-gray-700 ${
									validationErrors.contactNumber
										? 'border-red-500'
										: 'border-gray-300'
								}`}
							/>
						</div>
					</div>
					{validationErrors.contactNumber && (
						<div className="mt-1 text-sm text-red-600 flex items-start gap-1">
							<svg
								className="w-4 h-4 mt-0.5 flex-shrink-0"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fillRule="evenodd"
									d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
									clipRule="evenodd"
								/>
							</svg>
							<span className="break-words flex-1">
								{validationErrors.contactNumber}
							</span>
						</div>
					)}
				</div>

				{/* Password Field */}
				<div>
					<label
						htmlFor="password"
						className="block text-sm font-medium text-gray-700 mb-1"
					>
						Password
					</label>
					<div className="relative">
						<input
							type={passwordVisible ? 'text' : 'password'}
							id="password"
							name="password"
							placeholder="Create a password"
							value={formData.password}
							onChange={handleChange}
							required
							className={`block w-full border rounded-md shadow-sm p-3 focus:ring-purple-500 focus:border-purple-500 text-gray-700 pr-10 ${
								validationErrors.password ? 'border-red-500' : 'border-gray-300'
							}`}
						/>
						<button
							type="button"
							className="absolute inset-y-0 right-0 pr-3 flex items-center"
							onClick={() => setPasswordVisible(!passwordVisible)}
							aria-label={passwordVisible ? 'Hide password' : 'Show password'}
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
						</button>
					</div>

					{/* Password Strength Indicator */}
					{formData.password && (
						<div className="mt-2">
							<div className="flex items-center justify-between mb-1">
								<span className="text-xs text-gray-600">
									Password strength:
								</span>
								<span className="text-xs font-medium">
									{passwordStrength < 40
										? 'Weak'
										: passwordStrength < 80
										? 'Fair'
										: passwordStrength > 149
										? 'Very Strong'
										: 'Strong'}
								</span>
							</div>
							<div className="w-full bg-gray-200 rounded-full h-1.5">
								<div
									className={`h-1.5 rounded-full ${getPasswordStrengthColor()}`}
									style={{ width: `${passwordStrength}%` }}
								/>
							</div>
						</div>
					)}

					{validationErrors.password && (
						<div className="mt-2 text-sm text-red-600 flex items-start gap-1">
							<svg
								className="w-4 h-4 mt-0.5 flex-shrink-0"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fillRule="evenodd"
									d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
									clipRule="evenodd"
								/>
							</svg>
							<div className="flex-1">
								<span className="break-words">{validationErrors.password}</span>
								{formData.password && !validationErrors.password && (
									<div className="mt-1 text-green-600 flex items-center gap-1">
										<svg
											className="w-4 h-4"
											fill="currentColor"
											viewBox="0 0 20 20"
										>
											<path
												fillRule="evenodd"
												d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
												clipRule="evenodd"
											/>
										</svg>
										<span>Strong password!</span>
									</div>
								)}
							</div>
						</div>
					)}

					{passwordStrength < 80 && (
						<p className="mt-2 text-sm text-gray-500">
							Must contain uppercase, lowercase, number, special character, and
							be at least 8 characters.
						</p>
					)}
				</div>

				{/* Confirm Password Field */}
				<div>
					<label
						htmlFor="confirmPassword"
						className="block text-sm font-medium text-gray-700 mb-1"
					>
						Confirm Password
					</label>
					<div className="relative">
						<input
							type={confirmPasswordVisible ? 'text' : 'password'}
							id="confirmPassword"
							name="confirmPassword"
							placeholder="Retype password"
							value={formData.confirmPassword}
							onChange={handleChange}
							required
							className={`block w-full border rounded-md shadow-sm p-3 focus:ring-purple-500 focus:border-purple-500 text-gray-700 pr-10 ${
								validationErrors.confirmPassword
									? 'border-red-500'
									: 'border-gray-300'
							}`}
						/>
						<button
							type="button"
							className="absolute inset-y-0 right-0 pr-3 flex items-center"
							onClick={() => setConfirmPasswordVisible(!confirmPasswordVisible)}
							aria-label={
								confirmPasswordVisible ? 'Hide password' : 'Show password'
							}
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
										confirmPasswordVisible
											? 'M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.988 9.988 0 013.91-4.704M15 12a3 3 0 11-6 0 3 3 0 016 0z'
											: 'M15 12a3 3 0 11-6 0 3 3 0 016 0zM2.458 12C3.732 7.086 7.523 4 12 4s8.268 3.086 9.542 8c-1.274 4.914-5.065 8-9.542 8s-8.268-3.086-9.542-8z'
									}
								/>
							</svg>
						</button>
					</div>
					{validationErrors.confirmPassword && (
						<div className="mt-1 text-sm text-red-600 flex items-start gap-1">
							<svg
								className="w-4 h-4 mt-0.5 flex-shrink-0"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fillRule="evenodd"
									d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
									clipRule="evenodd"
								/>
							</svg>
							<span className="break-words flex-1">
								{validationErrors.confirmPassword}
							</span>
						</div>
					)}
					{!validationErrors.confirmPassword &&
						formData.confirmPassword &&
						formData.password === formData.confirmPassword && (
							<div className="mt-1 text-sm text-green-600 flex items-center gap-1">
								<svg
									className="w-4 h-4"
									fill="currentColor"
									viewBox="0 0 20 20"
								>
									<path
										fillRule="evenodd"
										d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
										clipRule="evenodd"
									/>
								</svg>
								<span>Passwords match!</span>
							</div>
						)}
				</div>

				{/* Terms Checkbox */}
				<div className="flex items-start pt-2">
					<input
						id="agreedToTerms"
						name="agreedToTerms"
						type="checkbox"
						checked={formData.agreedToTerms}
						onChange={handleChange}
						required
						className="h-5 w-5 text-purple-600 focus:ring-purple-500 border-gray-300 rounded mt-0.5 flex-shrink-0"
					/>
					<label
						htmlFor="agreedToTerms"
						className="ml-3 block text-sm text-gray-900 break-words"
					>
						By checking this box and clicking Sign up, you acknowledge and agree
						to our{' '}
						<Link
							href="#privacy-policy"
							className="text-purple-600 hover:text-purple-500 underline"
						>
							Privacy Policy
						</Link>
					</label>
				</div>

				{/* Submit Button */}
				<button
					type="submit"
					disabled={
						isSubmitting ||
						!formData.agreedToTerms ||
						Object.keys(validationErrors).length > 0
					}
					className={`w-full py-3 px-4 rounded-lg text-white font-semibold text-lg transition-all ${
						isSubmitting ||
						!formData.agreedToTerms ||
						Object.keys(validationErrors).length > 0
							? 'opacity-50 cursor-not-allowed'
							: 'hover:opacity-90 active:scale-[0.98]'
					}`}
					style={{
						background: 'linear-gradient(to right, #6D28D9, #A78BFA)',
					}}
				>
					{isSubmitting ? 'Creating Account...' : 'Sign Up'}
				</button>
			</form>

			<div className="mt-6 text-center text-gray-600">
				Already have an account?{' '}
				<Link href="/signin" className="text-purple-600 hover:text-purple-500">
					Sign In
				</Link>
			</div>

			{showSuccessPopup && (
				<RegistrationSuccessPopup
					userName={registeredUserName}
					onClose={() => setShowSuccessPopup(false)}
					autoCloseDelay={7000}
					homepagePath={homePagePath}
					homePageName={homePageName}
				/>
			)}
		</div>
	);
};

export default SignupForm;
