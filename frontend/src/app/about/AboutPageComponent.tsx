import Image from 'next/image';
import React from 'react';
import { Mail, Linkedin, Instagram, X, Facebook, Globe } from 'lucide-react';
import { footerData } from '@/staticData/footerData';

export default async function AboutPageComponent() {
	const x = footerData.twitterHandle;
	const fb = footerData.facebookHandle;
	const liI = footerData.linkedInHandle;
	const ig = footerData.instagramHandle;
	return (
		<main className="min-h-screen bg-gray-50 text-gray-800">
			<div className="container mx-auto px-4 py-12 max-w-4xl">
				{/* Header Section */}
				<header className="text-center mb-16">
					<h1 className="text-4xl md:text-5xl font-extrabold text-indigo-700 mb-4 tracking-tight">
						About Startinbox
					</h1>
					<p className="text-base sm:text-xl text-gray-600 max-w-2xl mx-auto">
						Startinbox is an{' '}
						<strong className="font-semibold">
							AI-powered startup assistant
						</strong>{' '}
						that helps you validate your ideas, create launch content, and
						connect with opportunities all in one place.
					</p>
					<p className="mt-2 text-sm sm:text-lg font-medium text-indigo-500">
						Our goal is simple: to help founders and creators turn ideas into
						action faster, smarter, and more confidently.
					</p>
				</header>

				{/* Why We Exist Section */}
				<section className="mb-16 p-8 bg-white rounded-xl shadow-lg border-l-4 border-indigo-500">
					<h2 className="text-3xl font-bold text-indigo-700 mb-4 flex items-center">
						Why We Exist
					</h2>
					<p className="text-gray-700 leading-relaxed">
						Every day, millions of great startup ideas never see the light of
						day because founders lack time, technical skills, or access to
						validation tools.
						<strong className="font-semibold">
							We built Startinbox to change that.
						</strong>
					</p>
					<p className="mt-4 text-gray-700 leading-relaxed">
						With our AI, anyone from students to solo founders can test their
						ideas, get feedback, and launch without needing a full team or huge
						budget.
					</p>
				</section>

				{/* What We Do Section */}
				<section className="mb-16">
					<h2 className="text-3xl font-bold text-indigo-700 mb-6 flex items-center">
						What We Do
					</h2>
					<div className="space-y-6">
						<div className="p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition duration-300">
							<h3 className="text-xl font-semibold text-gray-900 mb-2">
								AI-Powered Validation
							</h3>
							<p className="text-gray-700">
								Instantly analyzes your startup idea with a detailed lean canvas
								and score.
							</p>
						</div>
						<div className="p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition duration-300">
							<h3 className="text-xl font-semibold text-gray-900 mb-2">
								Launch Content Generation
							</h3>
							<p className="text-gray-700">
								Creates copy for your landing page, tweets, and pitches in
								minutes
							</p>
						</div>
						<div className="p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition duration-300">
							<h3 className="text-xl font-semibold text-gray-900 mb-2">
								Influencer Outreach Templates
							</h3>
							<p className="text-gray-700">
								Pre-written DMs to connect with potential collaborators or
								customers
							</p>
						</div>
						<div className="p-6 bg-white rounded-lg shadow-md hover:shadow-xl transition duration-300">
							<h3 className="text-xl font-semibold text-gray-900 mb-2">
								Add-on Services
							</h3>
							<p className="text-gray-700">
								Expert consultations or product management support to bring your
								idea to life
							</p>
						</div>
					</div>
				</section>

				{/* Mission, Vision, and Story Grid */}
				<div className="grid md:grid-cols-2 gap-8 mb-16">
					{/* Our Mission */}
					<section className="p-8 bg-indigo-50 rounded-xl shadow-inner">
						<h2 className="text-3xl font-bold text-indigo-700 mb-4 flex items-center">
							Our Mission
						</h2>
						<p className="text-gray-700 leading-relaxed">
							To make startup validation simple, affordable, and globally
							accessible so anyone, anywhere, can build something that matters.
						</p>
					</section>

					{/* Our Vision */}
					<section className="p-8 bg-indigo-50 rounded-xl shadow-inner">
						<h2 className="text-3xl font-bold text-indigo-700 mb-4 flex items-center">
							<span className="mr-3">💡</span> Our Vision
						</h2>
						<p className="text-gray-700 leading-relaxed">
							A world where great ideas don&apos;t die in notebooks but turn
							into thriving startups.
						</p>
					</section>
				</div>

				{/* Our Story Section */}
				<section className="mb-16 p-8 bg-white rounded-xl shadow-lg">
					<h2 className="text-3xl font-bold text-indigo-700 mb-4 flex items-center">
						Our Story
					</h2>
					<p className="text-gray-700 leading-relaxed">
						Startinbox was founded in 2025 by Ngozi Annastasia Njoku, a product
						manager passionate about helping people move from idea to execution.
					</p>
					<p className="mt-4 text-gray-700 leading-relaxed">
						After seeing how many founders struggle with early validation, she
						built Startinbox to make AI do the heavy lifting, turning research
						and content generation into a{' '}
						<strong className="font-semibold"> one-click process</strong>.
					</p>
					<div className="mt-6 flex justify-center">
						<Image
							src="https://res.cloudinary.com/ddqj8ejpa/image/upload/v1763556186/startinbox-CEO-2-copy-2_iurcpu.png"
							alt="Ngozi Annastasia Njoku, Founder of Startinbox"
							width={128}
							height={128}
							className="rounded-full object-cover shadow-lg border-4 border-indigo-100"
						/>
					</div>
				</section>

				{/* Join Our Journey / Contact Section */}
				<section className="text-center p-8 bg-indigo-600 text-white rounded-xl shadow-2xl">
					<h2 className="text-3xl font-bold mb-4">Join Our Journey</h2>
					<p className="text-lg mb-6 max-w-xl mx-auto">
						We&apos;re more than a product. We&apos;re a growing community of
						dreamers, builders, and innovators. Whether you&apos;re testing your
						first idea or planning your next startup, Startinbox is here to help
						you every step of the way.
					</p>

					<div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-8">
						{/* Email Contact */}
						<a
							href="mailto:contact@startinbox.tech"
							className="text-lg font-medium hover:text-indigo-200 transition duration-200 flex items-center"
						>
							<Mail className="w-5 h-5 mr-2" /> contact@startinbox.tech
						</a>

						{/* Social Media Links*/}
						<div className="flex space-x-4">
							<a
								href={`https://www.linkedin.com/${liI}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="LinkedIn"
								title="Follow us on LinkedIn"
								className="hover:text-indigo-200 transition duration-200"
							>
								<Linkedin className="w-6 h-6" />
							</a>
							<a
								href={`https://www.instagram.com/${ig}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="Instagram"
								title="Follow us on Instagram"
								className="hover:text-indigo-200 transition duration-200"
							>
								<Instagram className="w-6 h-6" />
							</a>
							<a
								href={`https://x.com/${x}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="X (formerly Twitter)"
								title="Follow us on X"
								className="hover:text-indigo-200 transition duration-200"
							>
								<X className="w-6 h-6" />
							</a>
							<a
								href={`https://web.facebook.com/${fb}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="Facebook"
								title="Follow us on Facebook"
								className="hover:text-indigo-200 transition duration-200"
							>
								<Facebook className="w-6 h-6" />
							</a>
						</div>
					</div>
				</section>
			</div>
		</main>
	);
}
