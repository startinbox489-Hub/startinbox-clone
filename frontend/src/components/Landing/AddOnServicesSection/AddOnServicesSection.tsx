import { AddOnServicesSectionProps } from './interface';
import Image from 'next/image';

const AddOnServicesSection = ({
	heading,
	subheading,
	services,
}: AddOnServicesSectionProps) => {
	return (
		<section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
			<div className="max-w-7xl mx-auto text-center mb-12">
				{/* Main Heading */}
				<h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight mb-3">
					{heading}
				</h2>
				{/* Subheading */}
				<p className="text-lg text-gray-600">{subheading}</p>
			</div>

			{/* Service Cards Container */}
			<div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
				{services.map((service, index) => (
					<div
						key={index}
						className="bg-white rounded-xl shadow-lg p-8 flex flex-col items-start text-left border border-gray-200"
					>
						{/* Icon/Image Placeholder */}
						<div className="w-16 h-16 mb-4">
							<Image
								src={service.iconSrc}
								alt={service.altText}
								className="w-full h-full object-contain"
								width={150}
								height={50}
							/>
							{/* <img src={service.iconSrc} alt={service.altText} className="w-full h-full object-contain" /> */}
						</div>

						{/* Title */}
						<h3 className="text-xl font-bold text-gray-900 mb-2">
							{service.title}
						</h3>

						{/* Price */}
						<p className="text-xl font-semibold text-purple-600 mb-6">
							{service.price}
						</p>

						{/* List of Items */}
						<ul className="space-y-3 text-gray-700">
							{service.items.map((item, itemIndex) => (
								<li key={itemIndex} className="flex items-center">
									<span className="text-purple-600 text-lg mr-2">•</span>{' '}
									{/* Custom bullet */}
									<span>{item.text}</span>
								</li>
							))}
						</ul>
					</div>
				))}
			</div>
		</section>
	);
};

export default AddOnServicesSection;
