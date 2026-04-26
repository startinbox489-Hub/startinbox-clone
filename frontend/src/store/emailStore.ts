import { PassedEmailState } from '@/types/users.types';
import { create } from 'zustand';

export const usePassedEmail = create<PassedEmailState>((set) => ({
	email: '',
	setEmail: (email) => set({ email }),
	clearEmail: () => set({ email: '' }),
}));
