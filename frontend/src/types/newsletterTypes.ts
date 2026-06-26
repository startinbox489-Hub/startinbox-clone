export interface UnsubscribeFormProps {
  initialHash: string;
}

export interface ConfirmationModalProps {
  onConfirm: () => void;
  onCancel: () => void;
  isLoading: boolean;
}

export interface LayoutProps {
  children: React.ReactNode;
}
