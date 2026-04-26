import Hero from '@/components/Landing/Hero/Hero';
import ValidateIdeaSection from '@/components/Landing/ValidateIdeaSection/ValidateIdeaSection';
import HowItWorksSection from '../components/Landing/HowItWorksSection/HowItWorksSection';
import Pricing from '@/components/Landing/Pricing/Pricing';
import { HowItWorksStepsData } from '@/staticData/howItWorksData';
import AllInOnePlatformSection from '@/components/Landing/AllInOnePlatformSection/AllInOnePlatformSection';
import { featureCardsData } from '@/staticData/allInOneData';
import AddOnServicesSection from '@/components/Landing/AddOnServicesSection/AddOnServicesSection';
import { addOnServicesData } from '@/staticData/addOnServicesData';
import FAQsSection from '@/components/Landing/FAQsSection/FAQsSection';
import NewsletterSection from '@/components/Landing/NewsletterSection/NewsletterSection';
import PricingService from '../lib/server/pricingService';
import FAQService from '@/lib/server/faqService';
import { getUserFromCookie } from '../lib/server/authService';
import PlansProvider from '@/components/client/PlanProvider';
import AddOnService from '@/lib/server/addOnService';
import { JWTPayload } from 'jose';
import { UserModel } from '@/types/users.types';
import { cookies } from 'next/headers';
import CreditsFeature from '@/components/Landing/CreditsFeatures/CreditsFeatures';
import TestimonialSlider2 from '@/components/Landing/Testimonial/Testimonial';

export default async function LandingPage() {
	const plans = await PricingService.getPricingPlans();
	const faqsData = await FAQService.getFAQs();
	const email = (await getUserFromCookie(false)) as JWTPayload;
	const addOns = await AddOnService.getAddOns();

	console.log(
		'landing page visit_count: ',
		(await cookies()).get('visit_count')?.value,
		', email: ',
		email?.email,
	);

	return (
		<div className="bg-white">
			{/* Hero Section */}
			{!email?.email && <Hero />}

			{/* Validate Idea Section */}
			<ValidateIdeaSection
				plans={plans.filter((p) => p.type === 'oneoff')}
				addOns={addOns}
				email={email ? (email.email as string) : null}
			/>

			<PlansProvider
				plans={plans}
				email={email ? (email.email as string) : null}
				user={email ? (email as unknown as UserModel) : undefined}
			/>

			{/* How It Works Section */}
			{!email && (
				<HowItWorksSection
					heading="THREE EASY STEPS"
					subheading="From idea spark to launch-ready, Here is how it works."
					steps={HowItWorksStepsData}
					ctaSubtext="YOUR FIRST IDEA IS ON US.😎"
					ctaButtonText="Start Free Trial"
					ctaButtonLink="#validate-idea-sec"
				/>
			)}

			{/* All In One Platform Section */}
			{!email && (
				<AllInOnePlatformSection
					heading="ALL-IN-ONE STARTUP LAUNCH PLATFORM"
					subheading="Everything you need to validate your idea and prepare for a successful launch"
					featureCards={featureCardsData}
				/>
			)}

			{/* Pricing Section */}
			<Pricing
				heading="SIMPLE AND TRANSPARENT PRICING"
				subheading="Choose a plan that matches your launch stage, there are no hidden fees, and you can cancel anytime."
				plans={plans}
			/>

			<CreditsFeature />

			{/* Add On Services Section */}
			<AddOnServicesSection
				heading="ADD-ON SERVICES (OPTIONAL)"
				subheading="Enhance your validation with expert support and hands-on execution."
				services={addOnServicesData}
			/>

			{/** Testimonials section */}
			{!email && <TestimonialSlider2 />}

			{/** Blog section */}

			{/* FAQs Section */}
			{!email && (
				<FAQsSection
					heading="FAQs"
					subheading="Enhance your validation with expert support and hands-on execution."
					faqs={faqsData}
				/>
			)}

			{/* <NewsletterSection /> */}
			{!email && <NewsletterSection />}
		</div>
	);
}
