import { ResultState } from '@/types/ourchaseTypes';

const UI_MAP: Record<
	ResultState,
	{
		label: string;
		subLabel?: string;
		intent: 'neutral' | 'info' | 'success' | 'warning' | 'error';
		progress?: number;
	}
> = {
	processing: {
		label: 'Processing payment',
		subLabel: 'Initializing secure checkout…',
		intent: 'info',
		progress: 20,
	},

	redirecting: {
		label: 'Redirecting',
		subLabel: 'Sending you to payment provider…',
		intent: 'info',
		progress: 35,
	},

	pending: {
		label: 'Payment pending',
		subLabel: 'Awaiting confirmation from provider…',
		intent: 'warning',
		progress: 55,
	},

	successful: {
		label: 'Payment successful',
		subLabel: 'Finalizing your access…',
		intent: 'success',
		progress: 100,
	},

	active_payment_detected: {
		label: 'Active Unused Payment detected',
		subLabel: 'Redirecting…',
		intent: 'success',
		progress: 100,
	},

	cancelled: {
		label: 'Payment cancelled',
		subLabel: 'Try again?',
		intent: 'neutral',
		progress: 100,
	},

	session_expired: {
		label: 'Session Expired',
		subLabel: 'Payment Took too long',
		intent: 'warning',
		progress: 100,
	},

	not_found: {
		label: 'Payment not found',
		subLabel: 'We could not locate this transaction.',
		intent: 'warning',
		progress: 60,
	},
	adds_on_error: {
		label: 'Adds-On Error',
		subLabel: '',
		intent: 'warning',
		progress: 60,
	},

	amount_discrepancy: {
		label: 'Amount discrepancy',
		subLabel: 'Charged amount does not match expected value.',
		intent: 'error',
		progress: 75,
	},

	signin_required: {
		label: 'Sign-in required',
		subLabel: 'Please authenticate to continue.',
		intent: 'neutral',
		progress: 40,
	},

	failed: {
		label: 'Payment failed',
		subLabel: 'No charge was completed.',
		intent: 'error',
		progress: 80,
	},

	timeout: {
		label: 'Verification timeout',
		subLabel: 'Unable to confirm payment in time.',
		intent: 'error',
		progress: 85,
	},

	server_error: {
		label: 'Server error',
		subLabel: 'An unexpected error occurred.',
		intent: 'error',
		progress: 90,
	},
};

const RETRY_CONFIG = {
	pending: {
		maxRetries: 3,
		delayMs: 5000,
		progressStart: 55,
		progressEnd: 80,
	},
	not_found: {
		maxRetries: 2,
		delayMs: 5000,
		progressStart: 60,
		progressEnd: 85,
	},
	timeout: {
		maxRetries: 1,
		delayMs: 6000,
		progressStart: 70,
		progressEnd: 90,
	},
};

export { UI_MAP, RETRY_CONFIG };
