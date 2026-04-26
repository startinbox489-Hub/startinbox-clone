import React from 'react';
import Image from 'next/image';
import { FooterProps } from '@/types/footer.type';

const Footer: React.FC<FooterProps> = ({
	quickLinks,
	companyLinks,
	contactEmail,
	twitterHandle,
	facebookHandle,
	instagramHandle,
	linkedInHandle,
}) => {
	const currentYear = new Date().getFullYear();

	return (
		<footer className="bg-black text-white py-12 px-6 sm:px-10 lg:px-20">
			<div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 border-b border-gray-700 pb-10">
				{/* Logo and Tagline */}
				<div className="col-span-1 md:col-span-1 flex flex-col items-start">
					<div className="mb-4">
						<Image
							src="/logo-white-svg-1.svg"
							alt="StartInBox Logo"
							width={150}
							height={50}
							className="h-auto  w-37"
						/>
					</div>
					<p className="text-gray-400 text-sm max-w-xs">
						Helping entrepreneurs validate ideas and launch successful startups
						faster and with confidence
					</p>
				</div>

				{/* Quick Links */}
				<div className="col-span-1">
					<h3 className="text-lg font-semibold mb-4">Quick Links</h3>
					<ul className="space-y-2">
						{quickLinks.map((link) => (
							<li key={link.href}>
								<a
									href={link.href}
									className="text-gray-400 hover:text-white transition-colors"
								>
									{link.label}
								</a>
							</li>
						))}
					</ul>
				</div>

				{/* Company */}
				<div className="col-span-1">
					<h3 className="text-lg font-semibold mb-4">Company</h3>
					<ul className="space-y-2">
						{companyLinks.map((link) => (
							<li key={link.href}>
								<a
									href={link.href}
									className="text-gray-400 hover:text-white transition-colors"
								>
									{link.label}
								</a>
							</li>
						))}
					</ul>
				</div>

				{/* Contact */}
				<div className="col-span-1">
					<h3 className="text-lg font-semibold mb-4 text-white">Contact</h3>
					<ul className="space-y-2">
						<li>
							<a
								href={`mailto:${contactEmail}`}
								className="text-gray-400 hover:text-white transition-colors"
							>
								{contactEmail}
							</a>
						</li>

						<li className="flex space-x-4 mt-4">
							{/* X / Twitter */}
							<a
								href={`https://x.com/${twitterHandle}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="Follow us on X"
								className="text-white hover:brightness-110 transition-all"
							>
								<svg
									fill="currentColor"
									viewBox="0 0 24 24"
									aria-hidden="true"
									className="h-6 w-6"
								>
									<path d="M18.244 2.25h3.308l-7.227 8.261 8.502 11.239H16.245l-6.27-8.067L4.92 21.75H1.61L9.66 12.044 1.254 2.25H4.29L10.327 9.77L18.244 2.25zM17.805 20.844h2.09L7.932 3.324H5.842L17.805 20.844z" />
								</svg>
							</a>

							{/* Facebook */}
							<a
								href={`https://web.facebook.com/${facebookHandle}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="Follow us on Facebook"
								className="text-[#1877F2] hover:brightness-110 transition-all"
							>
								<svg
									fill="currentColor"
									viewBox="0 0 24 24"
									aria-hidden="true"
									className="h-6 w-6"
								>
									<path d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 8.75 8.444 9.487v-6.985h-2.538v-2.497h2.538V9.309c0-2.511 1.488-3.656 3.79-3.656 1.092 0 2.24.195 2.24.195v2.46h-1.264c-1.248 0-1.637.77-1.637 1.564v1.864h2.793l-.447 2.497h-2.346v6.985C18.343 20.75 22 16.991 22 12z" />
								</svg>
							</a>

							{/* Instagram */}
							<a
								href={`https://www.instagram.com/${instagramHandle}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="Follow us on Instagram"
								className="text-[#E1306C] hover:brightness-110 transition-all"
							>
								<svg
									fill="currentColor"
									viewBox="0 0 24 24"
									aria-hidden="true"
									className="h-6 w-6"
								>
									<path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
								</svg>
							</a>

							{/* LinkedIn */}
							<a
								href={`https://www.linkedin.com/${linkedInHandle}`}
								target="_blank"
								rel="noopener noreferrer"
								aria-label="Follow us on LinkedIn"
								className="text-[#0077B5] hover:brightness-110 transition-all"
							>
								<svg
									fill="currentColor"
									viewBox="0 0 24 24"
									aria-hidden="true"
									className="h-6 w-6"
								>
									<path d="M4.98 3.5C4.98 4.604 4.078 5.5 2.99 5.5S1 4.604 1 3.5 1.902 1.5 2.99 1.5 4.98 2.396 4.98 3.5zM1 8.5h4v12H1v-12zm7 0h3.8v1.64h.05c.53-.95 1.83-1.96 3.77-1.96 4.03 0 4.78 2.52 4.78 5.8v6.52h-4v-5.77c0-1.38-.03-3.16-1.93-3.16-1.93 0-2.23 1.51-2.23 3.06v5.87h-4v-12z" />
								</svg>
							</a>
						</li>
					</ul>
				</div>
			</div>

			{/* Copyright */}
			<div className="max-w-7xl mx-auto pt-8 text-center md:text-left">
				<p className="text-gray-500 text-sm">
					© {currentYear} StartInBox. All rights reserved.
				</p>
			</div>
		</footer>
	);
};

export default Footer;
