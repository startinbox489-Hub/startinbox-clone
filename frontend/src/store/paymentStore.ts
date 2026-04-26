import { PaymentStoreStateI } from '@/types/paymentVerification.types';
import { create } from 'zustand';

export const usePaymentStateStore = create<PaymentStoreStateI>((set) => ({
	txReference: null,
	setTxReference: (txReference: string) => set({ txReference }),
	clearTxReference: () => set({ txReference: null }),
	paymentReference: null,
	setPaymentReference: (paymentReference: string) => set({ paymentReference }),
	clearPaymentReference: () => set({ paymentReference: null }),
}));
