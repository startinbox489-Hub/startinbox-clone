'use client';

import {
	createContext,
	useContext,
	useState,
	useEffect,
	ReactNode,
} from 'react';
import { UserModel } from '../types/users.types';
import { AuthContextType } from './interface';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
	const [user, setUser] = useState<UserModel | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const storedUser = localStorage.getItem('si_user');
		if (storedUser) {
			setUser(JSON.parse(storedUser));
		}
		setLoading(false);
	}, []);

	const signIn = (userData: UserModel) => {
		setUser(userData);
		localStorage.setItem('si_user', JSON.stringify(userData));
	};

	const signOut = () => {
		setUser(null);
		localStorage.removeItem('si_user');
	};

	const updateUser = (userData: Partial<UserModel>) => {
		if (user) {
			const updatedUser = { ...user, ...userData };
			setUser(updatedUser);
			localStorage.setItem('si_user', JSON.stringify(updatedUser));
		}
	};

	return (
		<AuthContext.Provider
			value={{ user, loading, signIn, signOut, updateUser }}
		>
			{children}
		</AuthContext.Provider>
	);
}

export function useAuth() {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error('useAuth must be used within an AuthProvider');
	}
	return context;
}
