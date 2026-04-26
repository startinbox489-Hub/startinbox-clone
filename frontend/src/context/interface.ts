import { UserModel } from '@/types/users.types';

export interface AuthContextType {
	user: UserModel | null;
	loading: boolean;
	signIn: (userData: UserModel) => void;
	signOut: () => void;
	updateUser: (userData: Partial<UserModel>) => void;
}
