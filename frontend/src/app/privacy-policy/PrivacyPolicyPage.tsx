'use server';

import React from 'react';
import {
	Mail,
	Clock,
	Shield,
	Database,
	Lock,
	AlertTriangle,
} from 'lucide-react';

const PrivacyPolicy = async () => {
	return (
		<main className="min-h-screen bg-gray-50 text-gray-800">
			<div className="container mx-auto px-4 py-12 max-w-4xl">
				{/* Header */}
				<header className="text-center mb-12 border-b pb-4">
					<h1 className="text-3xl sm:text-4xl font-extrabold text-indigo-700 mb-2">
						Startinbox Privacy Policy
					</h1>

					<div className="text-sm text-gray-500 flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-4">
						<span className="flex items-center">
							<Clock className="w-4 h-4 mr-1" />{' '}
							<strong>Effective Date:</strong> November 2025
						</span>

						<span className="flex items-center sm:hidden">|</span>

						<span className="flex items-center">
							<strong>Last Updated:</strong> November 2025
						</span>

						<span className="flex items-center sm:hidden">|</span>

						<span className="flex items-center">
							<strong>Owner:</strong> Startinbox
						</span>
					</div>
				</header>
				{/* 1. Introduction */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3 flex items-center">
						<Shield className="w-6 h-6 mr-2" /> 1. Introduction
					</h2>
					<p className="text-gray-700 leading-relaxed">
						Welcome to <strong>Startinbox</strong> — an AI-powered platform that
						helps founders, students, and creators validate startup ideas,
						generate launch content, and connect with startup resources.
					</p>
					<p className="mt-3 bg-indigo-50 p-3 border-l-4 border-indigo-500 rounded text-gray-700">
						This Privacy Policy explains how we collect, use, share, and protect
						your personal information when you use our services. By using
						Startinbox, you <strong>agree to this Privacy Policy</strong>.
					</p>
				</section>

				{/* 2. Information We Collect */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-4 flex items-center">
						<Database className="w-6 h-6 mr-2" /> 2. Information We Collect
					</h2>

					<h3 className="text-xl font-semibold mb-2">
						A. Information You Provide
					</h3>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4 mb-4">
						<li>
							<strong>Personal details:</strong> name, email address, WhatsApp
							number, and payment information (when applicable).
						</li>
						<li>
							<strong>Idea submission details:</strong> text or descriptions
							entered into our validation forms.
						</li>
						<li>
							<strong>Payment details:</strong> processed securely through
							third-party payment gateways (Paystack and Flutterwave). We do not
							store full card details.
						</li>
						<li>
							<strong>Newsletter information:</strong> email address and consent
							to receive marketing emails.
						</li>
						<li>
							<strong>Reviews/testimonials:</strong> your name (optional),
							feedback text, and rating.
						</li>
					</ul>

					<h3 className="text-xl font-semibold mb-2">
						B. Automatically Collected Data
					</h3>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
						<li>
							<strong>Device information:</strong> browser, operating system, IP
							address.
						</li>
						<li>
							<strong>Usage data:</strong> pages visited, time spent, actions
							taken.
						</li>
						<li>
							<strong>Cookies</strong> for analytics and user experience
							improvements.
						</li>
					</ul>
				</section>

				{/* 3. How We Use Your Information */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3">
						3. How We Use Your Information
					</h2>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
						<li>Deliver AI-generated idea validation reports and content.</li>
						<li>Process your payments securely.</li>
						<li>Communicate your results via email and WhatsApp.</li>
						<li>
							Send newsletters, product updates, and educational content (if you
							opt in).
						</li>
						<li>
							Display reviews/testimonials (only with your explicit consent).
						</li>
						<li>Improve our services and customer experience.</li>
						<li>Respond to inquiries, feedback, and support requests.</li>
						<li>Meet our legal and financial reporting obligations.</li>
					</ul>
				</section>

				{/* 4. Newsletter and Marketing Communications */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3">
						4. Newsletter and Marketing Communications
					</h2>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
						<li>You may subscribe to our newsletter voluntarily.</li>
						<li>We will only send content after you opt in.</li>
						<li>
							Every email includes an unsubscribe link that instantly removes
							you from the list.
						</li>
						<li>
							We may use trusted third-party providers such as SendGrid or
							MailerLite to manage newsletter delivery. These providers comply
							with GDPR and NDPR.
						</li>
					</ul>
				</section>

				{/* 5. Reviews and Testimonials */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3">
						5. Reviews and Testimonials
					</h2>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
						<li>
							By submitting a review, you grant Startinbox permission to display
							it publicly.
						</li>
						<li>
							Reviews include your first name, rating, and feedback. Including
							your startup name is optional.
						</li>
						<li>
							You can request removal or modification of your testimonial at any
							time by contacting us.
						</li>
					</ul>
				</section>

				{/* 6. Cookies and Tracking Technologies */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3">
						6. Cookies and Tracking Technologies
					</h2>
					<p className="text-gray-700 mb-3">
						We use cookies to enhance your experience, analyze traffic, and
						remember preferences.
					</p>
					<p className="text-sm text-gray-600">
						You can adjust your browser settings to refuse cookies, but some
						features may not function properly without them.
					</p>
				</section>

				{/* Data Security and Storage (7 & 8) */}
				<div className="grid md:grid-cols-2 gap-8 mb-8">
					<section className="p-6 bg-indigo-50 rounded-xl shadow-inner">
						<h2 className="text-xl font-bold text-indigo-700 mb-3 flex items-center">
							<Lock className="w-5 h-5 mr-2" /> 7. Data Storage and Security
						</h2>
						<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
							<li>
								All data is stored securely using encrypted databases
								(PostgreSQL, Google Cloud).
							</li>
							<li>We use HTTPS (SSL encryption) for all communication.</li>
							<li>
								We never sell, rent, or share your data with unauthorized third
								parties.
							</li>
							<li>We comply with GDPR and NDPR standards.</li>
						</ul>
					</section>

					<section className="p-6 bg-indigo-50 rounded-xl shadow-inner">
						<h2 className="text-xl font-bold text-indigo-700 mb-3">
							8. Payment Information
						</h2>
						<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
							<li>
								Payments are processed by Paystack and Flutterwave, both PCI-DSS
								compliant.
							</li>
							<li>
								Startinbox does not store or have access to your complete card
								information.
							</li>
							<li>
								We only retain transaction references, amounts, and timestamps
								for record-keeping.
							</li>
						</ul>
					</section>
				</div>

				{/* 9. Legal Basis for Processing */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3">
						9. Legal Basis for Processing (GDPR Compliance)
					</h2>
					<p className="text-gray-700 mb-3">
						Under the GDPR, we process your personal data on the following
						bases:
					</p>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
						<li>
							<strong>Contractual necessity:</strong> To provide services you
							request.
						</li>
						<li>
							<strong>Consent:</strong> For newsletters, marketing, and public
							reviews.
						</li>
						<li>
							<strong>Legitimate interest:</strong> To improve our platform and
							prevent fraud.
						</li>
						<li>
							<strong>Legal obligation:</strong> To comply with applicable tax
							and financial laws.
						</li>
					</ul>
				</section>

				{/* 10. Your Data Rights */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md border-l-4 border-indigo-500">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3">
						10. Your Data Rights
					</h2>
					<p className="text-gray-700 mb-3">
						As a user, you have the right to:
					</p>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
						<li>Access your personal data.</li>
						<li>Request correction of inaccuracies.</li>
						<li>Request deletion of your data (“Right to Be Forgotten”).</li>
						<li>
							Withdraw consent for newsletter or marketing communications.
						</li>
						<li>Request export of your data (data portability).</li>
						<li>File a complaint with a data protection authority.</li>
					</ul>
					<p className="mt-4 text-sm font-semibold text-indigo-600">
						To exercise these rights, email us at{' '}
						<a
							href="mailto:support@startinbox.tech"
							className="hover:text-indigo-800"
						>
							support@startinbox.tech
						</a>{' '}
						.
					</p>
				</section>

				{/* 11. Data Retention & 12. International Data Transfers */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3">
						11. Data Retention
					</h2>
					<ul className="list-disc list-inside space-y-2 text-gray-700 ml-4">
						<li>
							Idea submissions and reports are deleted after 12 months of
							inactivity.
						</li>
						<li>
							Newsletter and user account data are retained until you
							unsubscribe or request deletion.
						</li>
						<li>Backup copies may persist securely for up to 90 days.</li>
					</ul>

					<h2 className="text-2xl font-bold text-indigo-600 mt-6 mb-3">
						12. International Data Transfers
					</h2>
					<p className="text-gray-700">
						We may process data using cloud services that store information
						outside Nigeria. All transfers comply with Standard Contractual
						Clauses (SCCs) under GDPR for secure cross-border data protection.
					</p>
				</section>

				{/* 13. Children’s Privacy & 14. Changes to This Policy */}
				<section className="mb-8 p-6 bg-white rounded-lg shadow-md">
					<h2 className="text-2xl font-bold text-indigo-600 mb-3 flex items-center">
						<AlertTriangle className="w-6 h-6 mr-2" /> 13. Children’s Privacy
					</h2>
					<p className="text-gray-700 mb-4">
						Startinbox is not intended for users under 18 years old. We do not
						knowingly collect or store personal data from minors. If such data
						is identified, it will be deleted immediately upon notice.
					</p>

					<h2 className="text-2xl font-bold text-indigo-600 mt-6 mb-3">
						14. Changes to This Policy
					</h2>
					<p className="text-gray-700">
						We may update this Privacy Policy from time to time. We will notify
						users via email or in-app notice when significant changes occur. The
						updated version will be available at{' '}
						<a
							href="https://www.startinbox.tech/privacy-policy"
							className="text-indigo-600 hover:text-indigo-800"
						>
							www.startinbox.tech/privacy-policy
						</a>
						.
					</p>
				</section>

				{/* 15. Contact Information */}
				<section className="p-6 text-center bg-indigo-600 text-white rounded-xl shadow-lg">
					<h2 className="text-2xl font-bold mb-3">15. Contact Information</h2>
					<p className="mb-4">
						If you have questions, requests, or complaints about this Privacy
						Policy or your data, please contact us:
					</p>
					<p className="text-lg font-medium flex items-center justify-center">
						<Mail className="w-5 h-5 mr-2" />{' '}
						<a
							href="mailto:support@startinbox.tech"
							className="hover:text-indigo-200"
						>
							support@startinbox.tech
						</a>
					</p>
				</section>
			</div>
		</main>
	);
};

export default PrivacyPolicy;
