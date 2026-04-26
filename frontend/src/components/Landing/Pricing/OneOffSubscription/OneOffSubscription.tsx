'use client';

import { CheckIcon } from '@heroicons/react/20/solid';
import { IOneOffSubscriptionProps } from './interface';
import { useAuth } from '@/context/AuthProvider';

const OneOffSubscription = ({
	heading,
	subheading,
	plans,
}: IOneOffSubscriptionProps) => {
	const { user } = useAuth();
	return (
		<section
			id="pricing"
			className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50 pt-20"
		>
			<div className="max-w-7xl mx-auto text-center mb-12">
				{/* Main Heading */}
				<h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-3">
					{heading}
				</h2>
				{/* Subheading */}
				<p className="text-lg text-gray-600">{subheading}</p>
			</div>

			{/* Pricing Cards Container */}
			<div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
				{plans.map((plan) => (
						<div
							key={plan.name}
							className={`bg-white rounded-xl shadow-lg p-8 flex flex-col transition-all duration-300 ${
								plan.is_popular
									? 'border-2 border-purple-500 transform scale-105'
									: 'border border-gray-200'
							}`}
						>
							<div className="flex justify-between items-start mb-4">
								<h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
								{plan.is_popular && (
									<span className="bg-purple-100 text-purple-700 text-xs font-semibold px-3 py-1 rounded-full">
										Popular Plan
									</span>
								)}
							</div>
							<p className="text-4xl font-extrabold text-gray-900 mb-2">{`$${plan.price}`}</p>
							<p className="text-sm text-gray-600 min-h-[40px] mb-6">
								{plan.description}
							</p>{' '}
							{/* Min-height for alignment */}
							<ul className="space-y-3 mb-8 flex-grow">
								{plan.features.map((feature, index) => (
									<li key={index} className="flex items-center text-gray-700">
										<CheckIcon
											className="h-5 w-5 text-green-500 mr-2 flex-shrink-0"
											aria-hidden="true"
										/>
										<span>{feature.name}</span>
									</li>
								))}
							</ul>
							<a
								href={
									user?.email === null
										? plan.buttonLink
										: `/checkout/purchase?${plan.buttonLink.split('?')[1]}`
								}
								className={`block w-full text-center py-3 rounded-lg font-semibold text-lg transition-transform transform hover:scale-105 ${
									plan.is_popular
										? 'bg-gradient-to-r from-purple-700 to-indigo-500 text-white shadow-lg'
										: 'bg-gray-100 text-gray-800 hover:bg-gray-200'
								}`}
							>
								{plan.buttonText}
							</a>
						</div>
					))}
			</div>
		</section>
	);
};

export default OneOffSubscription;
