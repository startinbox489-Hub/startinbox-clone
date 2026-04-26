export interface PurchasePageProps {
	searchParams: Promise<{
		plan?: string;
		tx_ref?: string;
		transaction_id?: string;
		status:
			| 'success'
			| 'cancelled'
			| 'session_expired'
			| 'failed'
			| 'successful';
	}>;
}

export interface PurchaseComponentProps {
	plan?: number;
	genPdf: boolean;
	tx_ref?: string;
	transaction_id?: string;
	status?:
		| 'success'
		| 'cancelled'
		| 'session_expired'
		| 'failed'
		| 'successful';
}

export type ResultState =
	| 'processing'
	| 'redirecting'
	| 'successful'
	| 'failed'
	| 'pending'
	| 'not_found'
	| 'signin_required'
	| 'amount_discrepancy'
	| 'server_error'
	| 'timeout'
	| 'session_expired'
	| 'active_payment_detected'
	| 'cancelled'
	| 'adds_on_error';

export interface StatusProgressProps {
	label: string;
	subLabel?: string;
	progress?: number; // 0-100
	intent?: 'neutral' | 'success' | 'warning' | 'error' | 'info';
}
