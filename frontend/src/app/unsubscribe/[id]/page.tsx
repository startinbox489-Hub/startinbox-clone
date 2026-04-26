import { Suspense } from 'react';
import UnsubscribeForm from './UnsubscribeForm';
export const dynamic = 'force-dynamic';

const Unsubscribe = async ({ params }: { params: Promise<{ id: string }> }) => {
	const { id } = await params;

	return (
		<Suspense fallback={<div>Loading...</div>}>
			<UnsubscribeForm initialHash={id} />
		</Suspense>
	);
};

export default Unsubscribe;
