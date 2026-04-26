'use client';

import { StatusProgressProps } from '@/types/ourchaseTypes';
import clsx from 'clsx';

const INTENT_COLORS: Record<string, string> = {
	neutral: 'stroke-gray-400 text-gray-600',
	info: 'stroke-blue-500 text-blue-600',
	success: 'stroke-green-500 text-green-600',
	warning: 'stroke-yellow-500 text-yellow-600',
	error: 'stroke-red-500 text-red-600',
};

export default function StatusProgress({
	label,
	subLabel,
	progress,
	intent = 'neutral',
}: StatusProgressProps) {
	const radius = 36;
	const circumference = 2 * Math.PI * radius;
	const offset =
		progress !== undefined
			? circumference - (progress / 100) * circumference
			: circumference * 0.25;

	return (
		<div className="flex flex-col items-center justify-center gap-3 py-10">
			<svg width="96" height="96" className="rotate-[-90deg]">
				<circle
					cx="48"
					cy="48"
					r={radius}
					strokeWidth="6"
					fill="none"
					className="stroke-gray-200"
				/>
				<circle
					cx="48"
					cy="48"
					r={radius}
					strokeWidth="6"
					fill="none"
					strokeDasharray={circumference}
					strokeDashoffset={offset}
					strokeLinecap="round"
					className={clsx(
						INTENT_COLORS[intent],
						'transition-all duration-700 ease-out',
					)}
				/>
			</svg>

			<p className={clsx('text-base font-semibold', INTENT_COLORS[intent])}>
				{label}
			</p>

			{subLabel && (
				<p className="text-sm text-gray-500 text-center max-w-xs">{subLabel}</p>
			)}
		</div>
	);
}
