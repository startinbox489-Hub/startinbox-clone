'use client';

import { useState } from 'react';
import Image from 'next/image';
import { useRouter, useSearchParams } from 'next/navigation';

import { PostI } from '@/types/blogs.types';
import { track } from '@/lib/client/metaPixel';

export default function BlogList({
	posts,
	currentPage,
	totalPages,
}: {
	posts: PostI[];
	currentPage: number;
	totalPages: number;
}) {
	const [expandedPost, setExpandedPost] = useState<string | null>(null);
	const router = useRouter();
	const searchParams = useSearchParams();

	const event_id = track('ViewContent', {
		content_category: 'blog',
	});

	const handlePageChange = (page: number) => {
		const params = new URLSearchParams(searchParams.toString());
		params.set('page', page.toString());
		router.push(`/blogs?${params.toString()}`);
	};

	return (
		<div className="space-y-8">
			{posts.map((post) => {
				const isExpanded = expandedPost === post.id;
				return (
					<article
						key={post.id}
						className="bg-white shadow-lg rounded-2xl overflow-hidden transition-all duration-300"
					>
						{isExpanded ? (
							<>
								<div className="w-full h-64 relative">
									<Image
										src={post.image}
										alt={post.title}
										fill
										className="object-cover"
										priority
									/>
								</div>
								<div className="p-6">
									<div className="flex justify-between items-start mb-3">
										<h2 className="text-xl font-bold text-gray-900">
											{post.title}
										</h2>
										<span className="text-sm bg-gray-100 rounded-full px-3 py-1 text-gray-600">
											{new Date(post.date).toLocaleDateString('en-US', {
												month: 'short',
												day: 'numeric',
												year: 'numeric',
											})}
										</span>
									</div>
									<p className="text-gray-700 whitespace-pre-line">
										{post.content}
									</p>
									<button
										onClick={() => setExpandedPost(null)}
										className="text-blue-600 mt-4 font-medium hover:underline"
									>
										Read less
									</button>
								</div>
							</>
						) : (
							<div className="flex flex-col sm:flex-row p-6 gap-4">
								<div className="w-24 h-24 relative flex-shrink-0">
									<Image
										src={post.image}
										alt={post.title}
										fill
										className="object-cover rounded-lg"
										sizes="96px"
									/>
								</div>
								<div className="flex flex-col flex-1">
									<div className="flex justify-between items-start mb-2">
										<h2 className="text-lg font-bold text-gray-900">
											{post.title}
										</h2>
										<span className="text-sm bg-gray-100 rounded-full px-3 py-1 text-gray-600">
											{new Date(post.date).toLocaleDateString('en-US', {
												month: 'short',
												day: 'numeric',
												year: 'numeric',
											})}
										</span>
									</div>
									<p className="text-gray-700 line-clamp-3">
										{post.content.replace(/\n/g, ' ')}
									</p>
									<button
										onClick={() => setExpandedPost(post.id)}
										className="text-blue-600 mt-2 font-medium hover:underline self-start"
									>
										Read more
									</button>
								</div>
							</div>
						)}
					</article>
				);
			})}

			{/* Pagination */}
			{totalPages > 1 && (
				<div className="flex justify-center gap-2 mt-8">
					<button
						disabled={currentPage === 1}
						onClick={() => handlePageChange(currentPage - 1)}
						className="px-4 py-2 rounded-md border disabled:opacity-50 text-green-500"
					>
						Previous
					</button>
					<span className="px-4 py-2  text-black">
						{currentPage} / {totalPages}
					</span>
					<button
						disabled={currentPage === totalPages}
						onClick={() => handlePageChange(currentPage + 1)}
						className="px-4 py-2 rounded-md border disabled:opacity-50  text-red-500"
					>
						Next
					</button>
				</div>
			)}
		</div>
	);
}
