import { IdeaModelI } from "@/components/Landing/ValidateIdeaSection/interface";

export interface ApiInitiatePayResponseI {
  status: string;
  message: string;
  data: {
    subscription_plan_id?: string; // sub plan paid for
    has_active_payment: boolean; // if user has an active unused payment
    payment_link: string; // for checkout
    payment_reference?: string; // custom backend reference
    tx_reference?: string; // provider reference
    gen_pdf?: boolean;
  };
}

export interface ApiVerifyPayResponseI {
  status: string; // success/failed/not found/pending
  message: string;
  data: {
    payment_reference?: string; // custom backend reference
    provider?: string; // stripe or flutterwave
    subscription_plan_id?: string; // sub plan paid for
    subscription_plan_idx?: number; // sub plan idx for
    status: string; // payment status. e.g success/successful/approved/paid/failed/not found/pending
    tx_reference?: string; // provider reference
    amount?: string;
  };
  gen_pdf?: boolean;
}
export interface ApiValidationResponseI {
  status: string; // success/error
  message: string; // Suggestions generated succesfully
  idea: IdeaModelI | null;
}

export interface PaymentStoreStateI {
  txReference: string | null; // provider identifier
  setTxReference: (txReference: string) => void;
  clearTxReference: () => void;

  paymentReference: string | null; // custom identifier
  setPaymentReference: (paymentReference: string) => void;
  clearPaymentReference: () => void;
}
