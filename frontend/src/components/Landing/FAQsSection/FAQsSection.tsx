'use client';

import { useState } from 'react';
import { FAQsSectionProps } from './interface';

const FAQsSection = ({ heading, subheading, faqs }: FAQsSectionProps) => {
	const [openIndex, setOpenIndex] = useState<number | null>(null);

	const toggleAccordion = (index: number) => {
		setOpenIndex(openIndex === index ? null : index);
	};

	return (
		<section id="faq" className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
			<div className="max-w-7xl mx-auto text-center mb-12">
				<h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-3">
					{heading}
				</h2>
				<p className="text-lg text-gray-600">{subheading}</p>
			</div>

			<div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 text-left">
				{faqs.map((faq, index) => (
					<div
						key={index}
						className="flex flex-col border-b border-gray-200 py-4"
					>
						{/* Question */}
						<button
							onClick={() => toggleAccordion(index)}
							className="flex justify-between items-center text-xl font-semibold text-gray-900 w-full text-left focus:outline-none"
						>
							<span className="flex-1">{faq.question}</span>
							<span
								className={`transform transition-transform duration-300 ${
									openIndex === index ? 'rotate-180' : ''
								}`}
							>
								<svg
									className="h-6 w-6 text-gray-500"
									fill="none"
									viewBox="0 0 24 24"
									stroke="currentColor"
								>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										strokeWidth={2}
										d={
											openIndex === index
												? 'M18 12H6' // minus
												: 'M12 6v12m6-6H6' // plus
										}
									/>
								</svg>
							</span>
						</button>

						{/* Answer */}
						{openIndex === index && (
							<div className="mt-4 pr-12 text-gray-600">
								<p>{faq.answer}</p>
							</div>
						)}
					</div>
				))}
			</div>
		</section>
	);
};

export default FAQsSection;
