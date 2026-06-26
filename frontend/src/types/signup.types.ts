export interface RegistrationSuccessPopupProps {
  userName?: string;
  onClose: () => void;
  autoCloseDelay?: number; // Delay in milliseconds
  homepagePath?: string; // Path to the homepage, defaults to '/'
  homePageName: string;
}

export interface LoginAlertCardProps {
  title?: string;
  message?: string;
  signUpUrl?: string;
  signInUrl?: string;
  onClose: () => void;
}

export interface ValidationErrors {
  email?: string;
  contactNumber?: string;
  password?: string;
  confirmPassword?: string;
}
