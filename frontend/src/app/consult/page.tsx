'use client';

import { InlineWidget, useCalendlyEventListener } from 'react-calendly';

import { useRouter } from 'next/navigation';
import { ReactNode, useEffect, useState } from 'react';
import { CalendlyEvent } from 'react-calendly/typings/calendly';
import { useAuth } from '@/context/AuthProvider';
export const dynamic = 'force-dynamic';

export interface EventScheduledEventI {
	payload: {
		event: {
			[x: string]: ReactNode;
			uri: string;
		};
		invitee: {
			[x: string]: ReactNode;
			uri: string;
		};
	};
	event: CalendlyEvent.EVENT_SCHEDULED;
}

export default function SchedulePage() {
	const { user: AuthUser } = useAuth();
	const router = useRouter();
	const [finish, setFinish] = useState<string>('Finish');
	const [bookingDetails, setBookingDetails] =
		useState<EventScheduledEventI | null>(null);

	useEffect(() => {
		const isConsultingExists = localStorage.getItem('IsConsulting');
		const parsedIsConsultingExists = isConsultingExists
			? JSON.parse(isConsultingExists)
			: isConsultingExists;
		if (parsedIsConsultingExists) {
			if (parsedIsConsultingExists.isConsulting === false) {
				// console.log('is consulting: ', parsedIsConsultingExists.isConsulting);
				router.push('/analysis?i=1');
				return;
			}
		}

		const isConsulted = localStorage.getItem('IsConsulted');
		const parsedIsConsulted: { isConsulted: boolean } | null = isConsulted
			? JSON.parse(isConsulted)
			: isConsulted;
		if (parsedIsConsulted?.isConsulted) {
			// console.log('has consulted: ', parsedIsConsulted.isConsulted);
			router.push('/analysis?i=1');
			return;
		}
	}, [router]);

	useCalendlyEventListener({
		onEventScheduled: (e) => {
			// console.log('Booking consultant:', JSON.stringify(e.data));
			setBookingDetails(e.data); // contains event + invitee info
		},
		onDateAndTimeSelected: (e) => {
			console.log(
				'Calendly booking date selected:',
				JSON.stringify(e.data.event),
			);
		},
	});

	const handleFinish = () => {
		// console.log('bookingDetails 2: ', bookingDetails);

		setFinish('Loading Analysis...');
		localStorage.setItem('IsConsulted', JSON.stringify({ isConsulted: true }));
		router.push('/analysis?i=1');
	};

	return (
		<div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
			<h1 className="text-2xl font-bold mb-6 text-gray-900">
				Schedule Consultation on Calendly
			</h1>
			<InlineWidget
				url="https://calendly.com/startinbox489/30min"
				styles={{ minWidth: '100%', height: '600px' }}
				prefill={{
					...(AuthUser?.email && { email: AuthUser.email }),
					...(AuthUser?.first_name && { firstName: AuthUser.first_name }),
					...(AuthUser?.last_name && { lastName: AuthUser.last_name }),
				}}
			/>

			<div className="mt-6 flex justify-end">
				<button
					onClick={handleFinish}
					className="px-6 py-2 bg-blue-600 text-white rounded-md"
					disabled={
						!bookingDetails?.event ||
						!bookingDetails?.payload.event.uri ||
						!bookingDetails.payload.invitee.uri
					}
				>
					{finish}
				</button>
			</div>
		</div>
	);
}
