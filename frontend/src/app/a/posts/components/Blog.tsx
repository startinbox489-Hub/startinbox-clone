'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
	Edit2,
	Trash2,
	MoreVertical,
	FileText,
	Plus,
	Save,
	X,
} from 'lucide-react';
import { IBlogPost, IABlogPostProps } from './interface';
import { useRouter, useSearchParams } from 'next/navigation';
import Image from 'next/image';

const EMPTY_FORM: IBlogPost = {
	id: '',
	title: '',
	content: '',
	image: '',
	is_draft: true,
};

export default function Blog({ blogs }: IABlogPostProps) {
	const router = useRouter();
	const searchParams = useSearchParams();

	const [selectedBlog, setSelectedBlog] = useState<IBlogPost | null>(null);
	const [activeMenu, setActiveMenu] = useState<string | null>(null);
	const [isModalOpen, setIsModalOpen] = useState(false);
	const [loadingEdit, setLoadingEdit] = useState(false);
	const [formData, setFormData] = useState<IBlogPost>(EMPTY_FORM);

	const loadBlog = useCallback(async (id: string) => {
		const controller = new AbortController();

		try {
			const res = await fetch(`/api/v1/a/posts/${id}`, {
				credentials: 'include',
				signal: controller.signal,
			});

			if (res.ok) {
				const { data } = await res.json();
				setSelectedBlog(data);
			}
		} catch (err) {
			console.error('Fetch blog failed:', err);
		}

		return () => controller.abort();
	}, []);

	useEffect(() => {
		if (blogs?.data?.length) {
			loadBlog(blogs.data[0].id);
		}
	}, [blogs.data, loadBlog]);

	const handlePageChange = useCallback(
		(page: number) => {
			const params = new URLSearchParams(searchParams.toString());
			params.set('page', String(page));
			router.push(`/a/posts?${params}`);
		},
		[router, searchParams],
	);

	const handleDelete = useCallback(
		async (id: string) => {
			if (!confirm('Delete this post?')) return;

			try {
				const res = await fetch(`/api/v1/a/posts/${id}`, {
					method: 'DELETE',
				});

				if (!res.ok) return;

				const remaining = blogs?.data?.filter((b) => b.id !== id);

				if (selectedBlog?.id === id && remaining?.length) {
					loadBlog(remaining[0].id);
				}

				router.refresh();
			} catch (err) {
				console.error('Delete failed:', err);
			}
		},
		[blogs?.data, selectedBlog, router, loadBlog],
	);

	/* ---------------- Modal ---------------- */

	const openModal = async (blog?: IBlogPost) => {
		setActiveMenu(null);
		setIsModalOpen(true);

		if (!blog) {
			setFormData(EMPTY_FORM);
			return;
		}

		setLoadingEdit(true);

		try {
			const res = await fetch(`/api/v1/a/posts/${blog.id}`);
			if (res.ok) {
				const { data } = await res.json();
				setFormData(data);
			}
		} finally {
			setLoadingEdit(false);
		}
	};

	/* ---------------- Form ---------------- */

	const handleInputChange = (
		e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
	) => {
		const { name, value, type } = e.target as HTMLInputElement;

		setFormData((prev) => ({
			...prev,
			[name]:
				type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
		}));
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();

		const isEdit = Boolean(formData.id);
		const url = isEdit ? `/api/v1/a/posts/${formData.id}` : `/api/v1/a/posts`;

		const payload = {
			title: formData.title,
			content: formData.content,
			is_draft: formData.is_draft,
			...(formData.image?.trim() && { image: formData.image }),
		};

		try {
			const res = await fetch(url, {
				method: isEdit ? 'PUT' : 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload),
			});

			if (res.ok) {
				setIsModalOpen(false);
				router.refresh();
				return;
			}
			const data = await res.json();
			if (res.status === 422) {
				const message = data?.data?.msg;
				alert(
					JSON.stringify(
						message?.replace('String', 'content') || 'validation failed',
					),
				);
			}
		} catch (err) {
			console.error('Save failed:', err);
		}
	};

	/* ---------------- Render ---------------- */

	return (
		<div className="flex h-screen bg-gray-50 mt-18">
			{/* Sidebar */}
			<aside className="w-1/3 bg-white border-r overflow-y-auto">
				<div className="p-4 flex justify-between border-b">
					<h1 className="font-bold text-black">Blog Posts</h1>
					<button
						onClick={() => openModal()}
						className="bg-blue-600 text-white px-3 py-2 rounded"
					>
						<Plus size={14} /> Add Blog
					</button>
				</div>

				<ul>
					{blogs?.data?.map((blog) => (
						<li
							key={blog.id}
							onClick={() => loadBlog(blog.id)}
							className={`p-4 cursor-pointer border-b ${
								selectedBlog?.id === blog.id
									? 'bg-blue-50 border-r-4 border-blue-500'
									: 'hover:bg-gray-50'
							}`}
						>
							<div className="flex justify-between">
								<div>
									<p className="font-semibold text-black">{blog.title}</p>
									<span className="text-xs text-gray-400">{blog.date}</span>
								</div>

								<button
									onClick={(e) => {
										e.stopPropagation();
										setActiveMenu(blog.id === activeMenu ? null : blog.id);
									}}
									className="bg-amber-600 border-2"
								>
									<MoreVertical size={16} />
								</button>
							</div>

							{activeMenu === blog.id && (
								<div className="bg-white shadow border mt-2 rounded">
									<button
										onClick={() => openModal(blog)}
										className="block w-full px-3 py-2 text-left text-green-400"
									>
										<Edit2 size={14} /> Edit
									</button>

									<button
										onClick={() => handleDelete(blog.id)}
										className="block w-full px-3 py-2 text-left text-red-600"
									>
										<Trash2 size={14} /> Delete
									</button>
								</div>
							)}
						</li>
					))}
				</ul>
				{/* Pagination */}
				{blogs && blogs.pages > 1 && (
					<div className="flex justify-center gap-2 mt-8">
						<button
							disabled={blogs.page === 1}
							onClick={() => handlePageChange(blogs.page - 1)}
							className="px-4 py-2 rounded-md border disabled:opacity-50 text-green-500"
						>
							Previous
						</button>
						<span className="px-4 py-2  text-black">
							{blogs.page} / {blogs.pages}
						</span>
						<button
							disabled={blogs.page === blogs.pages}
							onClick={() => handlePageChange(blogs.page + 1)}
							className="px-4 py-2 rounded-md border disabled:opacity-50  text-red-500"
						>
							Next
						</button>
					</div>
				)}
			</aside>

			{/* Content */}
			<main className="flex-1 p-10 overflow-y-auto">
				{selectedBlog ? (
					<article className="max-w-2xl mx-auto">
						{selectedBlog.image && (
							<Image
								src={selectedBlog.image}
								alt="cover"
								width={600}
								height={300}
								className="rounded mb-6"
							/>
						)}

						<h1 className="text-3xl font-bold">{selectedBlog.title}</h1>
						<p className="text-gray-400">{selectedBlog.date}</p>

						<div className="mt-4 text-gray-700">{selectedBlog.content}</div>
					</article>
				) : (
					<div className="h-full flex items-center justify-center text-gray-400">
						<FileText size={40} />
					</div>
				)}
			</main>

			{/* Modal */}
			{isModalOpen && (
				<div className="fixed inset-0 bg-black/40 flex items-center justify-center">
					<form
						onSubmit={handleSubmit}
						className="bg-white p-6 rounded w-full max-w-xl space-y-4"
					>
						<div className="flex justify-between">
							<h2 className=" text-black">
								{formData.id ? 'Edit Post' : 'Create Post'}
							</h2>
							<button onClick={() => setIsModalOpen(false)}>
								<X color="black" />
							</button>
						</div>

						<input
							name="title"
							required
							value={formData.title}
							onChange={handleInputChange}
							placeholder="Title"
							className="w-full border p-2 rounded text-black"
						/>

						<input
							name="image"
							value={formData.image}
							onChange={handleInputChange}
							placeholder="Image URL"
							className="w-full border p-2 rounded text-black"
						/>

						<textarea
							name="content"
							rows={6}
							required
							value={loadingEdit ? 'Loading...' : formData.content}
							onChange={handleInputChange}
							className="w-full border p-2 rounded text-black"
						/>

						<label className="flex gap-2">
							<input
								type="checkbox"
								name="is_draft"
								checked={formData.is_draft}
								onChange={handleInputChange}
								className=" text-black"
							/>
							<div className=" text-black">Save as draft</div>
						</label>

						<button
							type="submit"
							className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2"
						>
							<Save size={14} /> Save
						</button>
					</form>
				</div>
			)}
		</div>
	);
}
