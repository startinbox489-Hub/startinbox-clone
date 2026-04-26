'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';

import {
	IProjectDetails,
	ProjectDetailsFormProps,
} from '@/types/projectDetails.types';
import SuccessPopup from './SuccessPopup';

export default function ProjectDetailsForm({
	ideaId,
}: ProjectDetailsFormProps) {
	const router = useRouter();
	const [proceed, setProceed] = useState<string>('Proceed');
	const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
	const [projectDetails, setProjectDetails] = useState<IProjectDetails>({
		projectType: '',
		projectStage: '',
		desiredStartDate: '',
	});
	const [projectTypeError, setProjectTypeError] = useState<string | null>(null);
	const [projectStageError, setProjectStageError] = useState<string | null>(
		null,
	);
	const [desiredStartDateError, setDesiredStartDateError] = useState<
		string | null
	>(null);

	const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const { name, value } = e.target;
		if (name === 'projectType') {
			if (value.trim().length < 3) {
				setProjectTypeError('Project Type is too short');
			} else {
				setProjectTypeError(null);
			}
		}
		if (name === 'projectStage') {
			if (value.trim().length < 3) {
				setProjectStageError('Project Stage is too short');
			} else {
				setProjectStageError(null);
			}
		}
		if (name === 'desiredStartDate') {
			if (value.trim().length < 10) {
				setDesiredStartDateError('Please select a Date');
			} else {
				setDesiredStartDateError(null);
			}
		}
		setProjectDetails((prev) => ({ ...prev, [name]: value }));
	};

	const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		for (const [_, value] of Object.entries(projectDetails)) {
			if (value.length < 3) {
				return;
			}
		}
		setProceed('Updating...');

		console.log('Project details:', projectDetails);
		const response = await fetch('/api/v1/idea-next-steps', {
			method: 'POST',
			credentials: 'include',
			body: JSON.stringify({
				idea_id: ideaId,
				project_type: projectDetails.projectType,
				project_stage: projectDetails.projectStage,
				desired_date: projectDetails.desiredStartDate,
			}),
			headers: { 'Content-Type': 'application/json' },
		});
		// const data = await response.json();
		if (response.ok) {
			setIsSubmitted(true);
			return;
		} else if (response.status === 422) {
			// console.error('idea-next-step 422: ', data);
			setIsSubmitted(false);
			return;
		} else if (response.status === 404) {
			// console.error('idea with id not found: ', data);
			setProceed('Redirecting to Analysis...');
			router.push('/analysis?i=1');
			setIsSubmitted(false);
			return;
		} else if (response.status === 409) {
			// console.error('idea-next-step already recorded for the idea: ', data);
			setIsSubmitted(false);
			setProceed('Already Recorded');
			router.push('/analysis?i=1');
			return;
		} else if (response.status === 401) {
			setIsSubmitted(false);
			console.log('Unauthorized');
			router.push(`/signin?next=${encodeURIComponent('next-step')}`);
			return;
		}
	};

	return (
		<>
			{!isSubmitted && (
				<form onSubmit={handleSubmit} className="space-y-6">
					{/* Project Type */}
					<div>
						<label
							htmlFor="projectType"
							className="block text-sm font-medium text-gray-700"
						>
							Project type
						</label>
						{projectTypeError && (
							<div className="text-red-500">{projectTypeError}</div>
						)}
						<input
							type="text"
							id="projectType"
							name="projectType"
							value={projectDetails.projectType}
							onChange={handleChange}
							required
							placeholder="e.g., Mobile App, Website, MVP"
							className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
						/>
					</div>

					{/* Project Stage */}
					<div>
						<label
							htmlFor="projectStage"
							className="block text-sm font-medium text-gray-700"
						>
							Project stage
						</label>
						{projectStageError && (
							<div className="text-red-500">{projectStageError}</div>
						)}
						<input
							type="text"
							id="projectStage"
							name="projectStage"
							value={projectDetails.projectStage}
							onChange={handleChange}
							required
							placeholder="e.g., Idea, Wireframes, Development"
							className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
						/>
					</div>

					{/* Desired Start Date */}
					<div>
						<label
							htmlFor="desiredStartDate"
							className="block text-sm font-medium text-gray-700"
						>
							Desired start date
						</label>
						{desiredStartDateError && (
							<div className="text-red-500">{desiredStartDateError}</div>
						)}
						<input
							type="date"
							id="desiredStartDate"
							name="desiredStartDate"
							value={projectDetails.desiredStartDate}
							onChange={handleChange}
							required
							placeholder="YYYY-MM-DD"
							pattern="\d{4}-\d{2}-\d{2}"
							className="mt-1 block w-full border border-gray-300 rounded-lg shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
						/>
						<p className="mt-2 text-sm text-gray-500">
							A message will be sent to your email/WhatsApp with your onboarding
							pack.
						</p>
					</div>

					<button
						type="submit"
						className="w-full text-white font-semibold py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-lg transition"
					>
						{proceed}
					</button>
				</form>
			)}

			{isSubmitted && <SuccessPopup />}
		</>
	);
}
