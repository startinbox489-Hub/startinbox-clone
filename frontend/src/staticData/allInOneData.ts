import { FeatureCard } from '@/types/allInOne.types';

export const featureCardsData: FeatureCard[] = [
	{
		iconSrc: '/brainstorm-skill.svg',
		altText: 'Idea Validation Icon',
		title: 'Idea Validation',
		description:
			'Get an idea score, detailed lean canvas, and customer persona within minutes.',
		items: [
			{ text: 'Idea Score (0-100)' },
			{ text: 'Lean Canvas with 9 blocks' },
			{ text: 'Ideal Customer Persona' },
			{ text: 'Startup Name Suggestions' },
		],
	},
	{
		iconSrc: '/rocket.svg',
		altText: 'Launch Content Icon',
		title: 'Launch Content',
		description:
			'Ready-to-use content for your website and social media platforms.',
		items: [
			{ text: 'Website Hero Section' },
			{ text: '3 Blog Post Outlines' },
			{ text: '5 Twitter Launch Posts' },
			{ text: 'Elevator Pitch Summary' },
		],
	},
	{
		iconSrc: '/popular-woman.svg',
		altText: 'Influencer Outreach Icon',
		title: 'Influencer Outreach',
		description: 'Connect with relevant influencers to promote your startup.',
		items: [
			{ text: 'Personalized DM Templates' },
			{ text: 'Niche Analysis' },
			{ text: 'Up to 3 Influencers' },
			{ text: 'Ready for Copy & Paste' },
		],
	},
];
