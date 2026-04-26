'use client';

import { useAuthStore } from '@/store/authStore';
import { UserModel } from '@/types/users.types';
import { useEffect } from 'react';

export interface AuthProviderProps {
  user: UserModel | null;
}

// receives the initial user data from a Server Component.
export default function AuthProvider({ user }: AuthProviderProps) {
  const signin = useAuthStore((state) => state.signin);

  useEffect(() => {
    // Hydrate the Zustand store with user data from the server.
    if (user) {
      signin(user);
    }
  }, [user, signin]);

  return null; // render nothing visible.
}
