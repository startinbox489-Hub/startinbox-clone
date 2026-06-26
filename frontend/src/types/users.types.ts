export interface UserModel {
  id: string;
  email: string;
  phone_number?: string | null;
  created_at?: string;
  updated_at?: string;
  first_name?: string | null;
  last_name?: string | null;
}

export interface TokensModel {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthState {
  user: UserModel | null;
  signin: (userModel: UserModel) => void;
  signout: () => void;
}

export interface PassedEmailState {
  email: string;
  setEmail: (email: string) => void;
  clearEmail: () => void;
}

export interface ApiUserData {
  user: null | UserModel;
  message: string;
}
