import { ICreditsFeatureData } from '@/components/Landing/CreditsFeatures/interface';

export const creditFeatures: ICreditsFeatureData[] = [
	{ text: '1 credit = 1 idea validation' },
	{ text: 'Credits are added instantly after payment' },
	{ text: 'Credits expire at the end of each billing cycle' },
	{ text: 'If you run out early, you can upgrade anytime' },
	{
		text: 'You keep your credits until your plan expires, even if you cancelled',
	},
];

export const creditFeaturesplans = [
	{
		name: 'Silver Plan',
		credits: 5,
		price: 12.99,
		period: 'week',
		description:
			'Perfect for active founders who validate ideas regularly and want a simple, flexible weekly billing cycle.',
		features: [
			'5 fresh ideas every week',
			'Credits expire after 7 days',
			'Auto-renew every 7 days',
			'Cancel anytime',
		],
		buttonText: 'Start Weekly Plan',
	},
	{
		name: 'Gold Plan',
		credits: 20,
		price: 39.99,
		period: 'month',
		description:
			'Best for founders testing multiple ideas each month and looking for the best balance of value and flexibility.',
		features: [
			'20 idea validation every month',
			'Credits expire in 30 days',
			'Auto-renew monthly',
			'Cancel anytime',
		],
		buttonText: 'Start Monthly Plan',
		isPopular: true,
	},
	{
		name: 'Diamond Plan',
		credits: 40,
		price: 99,
		period: 'month',
		description:
			'Designed for digital marketers, content creators, strategists, and agencies who validate ideas for their clients.',
		features: [
			'40 ideas every month',
			'Built for client projects and campaign',
			'Best value for high-volume users',
			'Auto-renew monthly',
			'Cancel anytime',
		],
		buttonText: 'Start Marketers Plan',
	},
];
