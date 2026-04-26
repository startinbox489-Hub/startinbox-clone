'use client';

import React, { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import UserMenuComponent from '../UserMenu';
import { useAuth } from '@/context/AuthProvider';
import { IUserActivePlan } from './interface';

const Header = () => {
	const { user: AuthUser } = useAuth();
	const [isOpen, setIsOpen] = useState<boolean>(false);

	useEffect(() => {
		const getUserPlans = async () => {
			const response = await fetch('/api/v1/plans/active', {
				method: 'GET',
				credentials: 'include',
			});
			if (response.status === 401) return;
			if (response.ok) {
				const data = (await response.json()).data as IUserActivePlan[];
				localStorage.setItem('si_user_plans', JSON.stringify(data)); // array
			}
		};
		if (AuthUser) {
			const userPlan = localStorage.getItem('si_user_plans'); // array
			if (!userPlan) {
				getUserPlans();
			}
		}
	}, [AuthUser]);

	return (
		<header className="fixed top-0 left-0 w-full bg-white shadow z-50">
			<nav className="container mx-auto flex justify-between items-center px-6 py-4">
				{/* Logo */}
				<div className="flex items-center gap-2">
					<Link href="/">
						<Image
							className="h-8 w-auto"
							src="/logo-svg-1.svg"
							alt="Startinbox Logo"
							width={180}
							height={38}
							priority
						/>
					</Link>
					<Link href="/" className="hover:text-indigo-600">
						<span className="font-bold text-lg text-gray-800">STARTINBOX</span>
					</Link>
				</div>

				{/* Desktop Links */}
				<ul className="hidden md:flex items-center gap-8 text-gray-700 font-medium">
					<li>
						<Link href="/" className="hover:text-indigo-600">
							Home
						</Link>
					</li>
					{AuthUser?.email ? null : (
						<li>
							<Link href="/#features" className="hover:text-indigo-600">
								Features
							</Link>
						</li>
					)}
					{AuthUser?.email ? null : (
						<li>
							<Link href="/#how-it-works" className="hover:text-indigo-600">
								How it works
							</Link>
						</li>
					)}
					{AuthUser?.email ? null : (
						<li>
							<Link href="/#pricing" className="hover:text-indigo-600">
								Pricing
							</Link>
						</li>
					)}
					<li>
						<Link href="/blogs" className="hover:text-indigo-600">
							Blogs
						</Link>
					</li>
				</ul>

				{/* Buttons (Desktop) */}
				<div className="hidden md:flex gap-4">
					<UserMenuComponent />
				</div>

				{/* Mobile Menu Button */}
				<button
					className="md:hidden p-2 rounded-md hover:bg-gray-100"
					onClick={() => setIsOpen(true)}
				>
					<Menu className="w-6 h-6 text-gray-700" />
				</button>
			</nav>

			{/* Mobile Drawer */}
			<div
				className={`fixed top-0 right-0 h-full w-64 bg-white shadow-lg transform transition-transform duration-300 z-50 ${
					isOpen ? 'translate-x-0' : 'translate-x-full'
				}`}
			>
				<div className="flex justify-between items-center px-6 py-4 border-b">
					<span className="font-bold text-lg text-gray-800">Menu</span>
					<button onClick={() => setIsOpen(false)}>
						<X className="w-6 h-6 text-gray-700" />
					</button>
				</div>

				<ul className="flex flex-col gap-6 px-6 py-6 text-gray-700 font-medium">
					<li>
						<Link href="/" onClick={() => setIsOpen(false)}>
							Home
						</Link>
					</li>
					{AuthUser?.email ? null : (
						<li>
							<Link href="/#features" onClick={() => setIsOpen(false)}>
								Features
							</Link>
						</li>
					)}
					{AuthUser?.email ? null : (
						<li>
							<Link href="/#how-it-works" onClick={() => setIsOpen(false)}>
								How it works
							</Link>
						</li>
					)}
					{AuthUser?.email ? null : (
						<li>
							<Link href="/#pricing" onClick={() => setIsOpen(false)}>
								Pricing
							</Link>
						</li>
					)}
					<li>
						<Link href="/blogs" onClick={() => setIsOpen(false)}>
							Blogs
						</Link>
					</li>
				</ul>

				<div className="px-6 mt-auto flex flex-col gap-4">
					<UserMenuComponent />
				</div>
			</div>

			{/* Backdrop */}
			{isOpen && (
				<div
					className="fixed inset-0 bg-black/30 z-40"
					onClick={() => setIsOpen(false)}
				/>
			)}
		</header>
	);
};

export default Header;
