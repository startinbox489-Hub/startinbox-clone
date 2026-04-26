'use client';

import NextImage from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

const words = [
	'STARTUP IDEA',
	'MARKET FIT',
	'BUSINESS MODEL',
	'LAUNCH STRATEGY',
];

export default function Hero() {
	const [index, setIndex] = useState(0);

	// Word rotation
	useEffect(() => {
		const t = setInterval(() => {
			setIndex((i) => (i + 1) % words.length);
		}, 2200);

		return () => clearInterval(t);
	}, []);

	// Cursor glow
	useEffect(() => {
		const glow = document.getElementById('cursor-glow');
		if (!glow) return;

		const move = (e: MouseEvent) => {
			glow.style.setProperty('--x', `${e.clientX}px`);
			glow.style.setProperty('--y', `${e.clientY}px`);
		};

		window.addEventListener('mousemove', move, { passive: true });

		return () => window.removeEventListener('mousemove', move);
	}, []);

	return (
		<section className="hero relative h-screen overflow-hidden flex items-center justify-center text-center">
			{/* Background */}
			<div
				className="absolute inset-0 bg-cover bg-center"
				style={{ backgroundImage: "url('/new-si-hero-image.png')" }}
			/>

			<div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/30 to-black/80" />

			<div id="cursor-glow" className="pointer-events-none absolute inset-0" />

			{/* Content */}
			<div className="hero-content relative z-10 max-w-4xl px-6 text-white animate-hero-in">
				{/* Badge */}
				<span className="inline-block px-6 py-2 rounded-full bg-white/90 text-black text-sm font-semibold mb-10">
					AI-Powered Startup Validation
				</span>

				{/* Headline */}
				<h1 className="text-4xl md:text-6xl font-extrabold leading-tight mb-8">
					<span className="block mb-2">VALIDATE YOUR</span>

					<span className="relative inline-block min-h-[70px]">
						<span key={index} className="block gradient-text animate-word">
							{words[index]}
						</span>
					</span>

					<span className="block mt-2">IN MINUTES</span>
				</h1>

				<p className="text-lg md:text-xl text-gray-200 max-w-2xl mx-auto mb-14">
					Validate your business idea fast before building. Test demand, get
					insights, and launch smarter.
				</p>

				{/* CTA */}
				<div className="flex flex-col md:flex-row gap-6 justify-center mb-16">
					<Link href="#validate-idea-sec">
						<button className="btn-primary">Try for Free</button>
					</Link>

					<Link href="#features">
						<button className="btn-secondary">Learn More</button>
					</Link>
				</div>

				{/* Trust */}
				<div className="flex items-center justify-center gap-4">
					<div className="flex -space-x-2">
						{[1, 2, 3].map((i) => (
							<NextImage
								key={i}
								src={`https://i.pravatar.cc/40?img=${i}`}
								alt="Founder"
								width={36}
								height={36}
								className="rounded-full border-2 border-white"
							/>
						))}
					</div>

					<p className="text-sm text-gray-300">
						Trusted by <span className="text-white font-bold">100+</span>{' '}
						founders
					</p>
				</div>
			</div>

			{/* Scroll Indicator */}
			<div className="absolute bottom-8 text-white/60 text-xs animate-scroll">
				Scroll ↓
			</div>
		</section>
	);
}
