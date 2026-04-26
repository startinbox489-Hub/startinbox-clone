import { creditFeatures } from '@/staticData/creditsFeatureData';

const CreditsFeature = () => {
	return (
		<section className="bg-white py-16 px-6 font-sans">
			<div className="flex flex-col justify-center align-items-center max-w-4xl mx-auto text-right">
				{/* Header */}
				<div className="flex flex-col justify-center align-items-center">
					<h2 className="text-5xl font-black text-slate-800 uppercase tracking-tight mb-4  text-center">
						How Credits Work
					</h2>
					<p className="lg:text-xl text-slate-600 mb-16 p-10  text-center">
						Choose a plan that matches your launch stage{' '}
						<span>— no hidden fees, cancel anytime.</span>
					</p>
				</div>

				<div className="flex md:gap-30">
					{/* Features List */}
					<div className="flex flex-col gap-12 items-start text-left w-full max-w-md">
						{creditFeatures.map((feature, index) => (
							<div key={index} className="flex items-center group">
								<div className="w-1.5 h-12 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full mr-8" />

								<span className="text-xl md:text-2xl text-blue-600 font-medium tracking-tight">
									{feature.text}
								</span>
							</div>
						))}
					</div>
					{/* Orb */}
					<div className="md:w-94 h-100 bg-gradient-to-br from-[#4A6CF7] to-[#9B66FF] rounded-t-[160px] rounded-br-[160px] rounded-bl-none mt-20" />
				</div>
			</div>
		</section>
	);
};

export default CreditsFeature;
