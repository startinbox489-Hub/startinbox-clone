import { AuthState } from '@/types/users.types';
import { create } from 'zustand';

export const useAuthStore = create<AuthState>((set) => ({
	user: null,
	signin: (userModel) => set({ user: userModel }),
	signout: () => set({ user: null }),
}));
