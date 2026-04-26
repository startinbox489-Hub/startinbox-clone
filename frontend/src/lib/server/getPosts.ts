import 'server-only';

import serverConfig from '../config/private';
import { ApiPostI, PostI } from '@/types/blogs.types';

export default class PostsService {
	static async getPosts(
		page: number,
		limit?: number,
		order?: string,
		orderBy?: string,
	): Promise<ApiPostI> {
		try {
			let url = `${await serverConfig(
				'BACKEND_BASE_URL',
			)}/api/v1/posts?page=${page}`;
			if (limit) {
				url = `${url}&limit=${limit}`;
			}
			if (order) {
				url = `${url}&order=${order}`;
			}
			if (orderBy) {
				url = `${url}&orderBy=${orderBy}`;
			}
			const response = await fetch(url, {
				method: 'GET',
			});
			const data: ApiPostI = await response.json();
			// console.log('data: ', JSON.stringify(data));

			return data;
		} catch (error) {
			console.error('error retrieving posts: ', error);
			throw error;
		}
	}
	static async getPost(
		postId: string,
	): Promise<{ message: string; status: string; data: PostI }> {
		try {
			const url = `${await serverConfig(
				'BACKEND_BASE_URL',
			)}/api/v1/posts/${postId}`;

			const response = await fetch(url, {
				method: 'GET',
			});
			const data = await response.json();
			// console.log('data: ', JSON.stringify(data));

			return data;
		} catch (error) {
			console.error('error retrieving post: ', error);
			throw error;
		}
	}
}
