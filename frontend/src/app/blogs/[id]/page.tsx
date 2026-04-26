import { track } from '@/lib/client/metaPixel';
import PostsService from '@/lib/server/getPosts';
import { PostI } from '@/types/blogs.types';
import Image from 'next/image';
import { Suspense } from 'react';

export const dynamic = 'force-dynamic';

export default async function BlogPostPage({
	params,
}: {
	params: Promise<{ id: string }>;
}) {
	const { id } = await params;
	let post: PostI = {
		id: '',
		title: '',
		date: '',
		image: '',
		content: '',
	};

	try {
		const data = await PostsService.getPost(id);

		if (data?.status === 'success') {
			post = data.data;
		}
	} catch (e) {
		console.error('error getting post:', e);
	}

	const _ = track('ViewContent', {
		content_type: 'blog',
		content_name: post.title,
	});

	return post?.id !== '' ? (
		<Suspense fallback={<div>Loading...</div>}>
			<div className="w-full flex justify-center px-4 md:px-0 mt-10 mb-20">
				<div className="max-w-4xl w-full">
					{/* Feature Image */}
					<div className="relative w-full h-64 md:h-96 rounded-xl overflow-hidden shadow">
						<Image
							src={post.image}
							alt={post.title}
							fill
							className="object-cover"
							priority
						/>
					</div>

					{/* Title + Date */}
					<div className="mt-8">
						<h1 className="text-2xl md:text-3xl font-bold text-gray-800">
							{post.title}
						</h1>
						<p className="text-sm text-gray-500 mt-2">{post.date}</p>
					</div>

					{/* Content */}
					<div className="mt-6 text-gray-700 leading-relaxed whitespace-pre-line">
						{post.content}
					</div>
				</div>
			</div>
		</Suspense>
	) : (
		<></>
	);
}
