export interface IUserActivePlan {
  id: string;
  is_current: boolean;
  subscription_plan_id: string;
  is_expired: boolean;
  flutterwave_subscription_id: number;
  credit_used: number;
  remaining_credits: number;
  type: string;
  name: string;
  idx: number;
}
