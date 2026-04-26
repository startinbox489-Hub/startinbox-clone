export interface IVerifyProps {
	searchParams: Promise<ISearchParams>;
}

export interface ISearchParams {
	status?: string;
	tx_ref?: string;
	transaction_id?: string;
}

export interface IPaymentSuccessProps {
	transactionId: string;
}

export interface IPaymentFailedProps {
	plan: number;
	verifyStatus?: string;
	errorMessage: string;
}

export interface IBillingProps {
	params: Promise<{ id: string }>;
	searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}
