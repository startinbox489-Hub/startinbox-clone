import { connection } from 'next/server';
import React from 'react';
import { Suspense } from 'react';

import AnalysisSection from '@/app/analysis/AnalysisSection';
import AddOnServicesSection from '@/components/Landing//AddOnServicesSection/AddOnServicesSection';
import { analysisAddOnServicesData } from '@/staticData/analysisData';
export const dynamic = 'force-dynamic';

export default async function AnalysisPage({
	searchParams,
}: {
	searchParams: Promise<{ i?: string; next?: string }>;
}) {
	await connection();
	return (
		<Suspense fallback={<>Loading Analysis...</>}>
			<div className="bg-white py-16 px-4 sm:px-6 lg:px-8">
				<div className="max-w-7xl mx-auto">
					<AnalysisSection searchParams={searchParams} />

					{/* Add-On Services Section */}
					<AddOnServicesSection
						heading={analysisAddOnServicesData.heading}
						subheading={analysisAddOnServicesData.subheading}
						services={analysisAddOnServicesData.services}
					/>
				</div>
			</div>
		</Suspense>
	);
}
