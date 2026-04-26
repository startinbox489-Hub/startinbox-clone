'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Search, ArrowLeft } from 'lucide-react';
import { useState, useMemo } from 'react';

const SUGGESTED_ROUTES = [
	{ label: 'Home', href: '/' },
	{ label: 'Pricing', href: '/pricing' },
	{ label: 'Blog', href: '/blogs' },
	{ label: 'FAQ', href: '/#faq' },
];

export default function NotFoundPage() {
	const router = useRouter();
	const [query, setQuery] = useState('');
	const [focused, setFocused] = useState(false);

	const handleSearch = (e: React.FormEvent) => {
		e.preventDefault();
		if (query.trim()) {
			router.push(`/search?q=${encodeURIComponent(query.trim())}`);
		}
	};

	// Filter routes based on the search query
	const filteredRoutes = useMemo(() => {
		if (!query.trim()) return SUGGESTED_ROUTES;
		return SUGGESTED_ROUTES.filter((r) =>
			r.label.toLowerCase().includes(query.toLowerCase()),
		);
	}, [query]);

	return (
		<div className="relative min-h-screen overflow-hidden bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center px-6 py-20 animate-fadeIn">
			{/* Floating shapes */}
			<div className="pointer-events-none absolute inset-0 overflow-hidden">
				<div className="floating-shape bg-blue-300/40 dark:bg-blue-500/20 w-40 h-40 rounded-full top-10 left-5"></div>
				<div className="floating-shape-delay bg-purple-300/40 dark:bg-purple-500/20 w-56 h-56 rounded-full bottom-20 right-10"></div>
				<div className="floating-shape bg-pink-300/40 dark:bg-pink-500/20 w-24 h-24 rounded-full bottom-10 left-1/4"></div>
			</div>

			{/* 404 large text */}
			<h1 className="text-7xl sm:text-8xl font-extrabold text-gray-900 dark:text-white mb-4 relative z-10">
				404
			</h1>

			<p className="text-lg sm:text-xl text-gray-600 dark:text-gray-300 mb-8 text-center max-w-md relative z-10">
				The page you are looking for doesn’t exist, but here are some helpful
				links.
			</p>

			{/* Search bar with suggestions */}
			<div className="w-full max-w-md relative z-20">
				<form
					onSubmit={handleSearch}
					className="flex items-center bg-white dark:bg-gray-800 shadow-md rounded-lg px-4 py-2 border border-gray-200 dark:border-gray-700"
				>
					<Search className="text-gray-400 dark:text-gray-500 w-5 h-5" />
					<input
						type="text"
						value={query}
						onChange={(e) => setQuery(e.target.value)}
						onFocus={() => setFocused(true)}
						onBlur={() => setTimeout(() => setFocused(false), 150)}
						placeholder="Search pages..."
						className="flex-1 px-3 py-2 outline-none text-gray-700 dark:text-gray-200 bg-transparent"
					/>
				</form>

				{/* Suggestions Dropdown */}
				{focused && (
					<div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-gray-800 shadow-xl rounded-lg border border-gray-200 dark:border-gray-700 max-h-64 overflow-y-auto animate-fadeIn">
						{filteredRoutes.length > 0 ? (
							filteredRoutes.map((route, i) => (
								<Link
									key={i}
									href={route.href}
									className="block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-800 dark:text-gray-200 border-b border-gray-100 dark:border-gray-700 last:border-none transition"
								>
									{route.label}
								</Link>
							))
						) : (
							<div className="px-4 py-3 text-gray-500 dark:text-gray-400">
								No matching sections found.
							</div>
						)}
					</div>
				)}
			</div>

			{/* Buttons */}
			<div className="flex mt-10 space-x-4 relative z-10">
				<Link
					href="/"
					className="inline-flex items-center px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg font-medium shadow hover:opacity-90 transition-all duration-150"
				>
					Go Home
				</Link>

				<button
					onClick={() => router.back()}
					className="inline-flex items-center px-6 py-3 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-lg font-medium shadow hover:bg-gray-100 dark:hover:bg-gray-700 transition-all duration-150"
				>
					<ArrowLeft className="w-4 h-4 mr-2" />
					Go Back
				</button>
			</div>
		</div>
	);
}
