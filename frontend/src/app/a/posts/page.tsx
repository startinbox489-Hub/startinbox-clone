import { Suspense } from 'react';
import Blog from './components/Blog';
import AdminPostsService from '@/lib/server/adminPosts';
import { redirect } from 'next/navigation';
export const dynamic = 'force-dynamic';

export default async function BlogPage({
	searchParams,
}: {
	searchParams: Promise<{ page?: string; limit?: string }>;
}) {
	const params = await searchParams;
	const { page, limit } = params;
	let path = '/api/v1/a/posts';
	if (page) path += `?page=${page}`;
	if (limit) path += `?limit=${limit}`;

	const response = await AdminPostsService.getPosts(path);
	const data =
		response.headers.get('content-type') === 'application/json'
			? await response.json()
			: await response.text();

	// console.log('res: ', data);
	if (response.status === 401)
		redirect(`/signin?next=${encodeURI('/a/posts')}`);
	if (response.status === 403) redirect('/');
	if (response.status > 499) {
		console.log('error fetching admin blogs: ', data);
		redirect('/');
	}

	return (
		<Suspense fallback={<div>Loading Posts...</div>}>
			<Blog blogs={data} page={page} limit={limit} />
		</Suspense>
	);
}
