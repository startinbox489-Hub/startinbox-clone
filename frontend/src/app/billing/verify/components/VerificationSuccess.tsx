import { CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { IPaymentSuccessProps } from "./interface";

export default function VerificationSuccess({
  transactionId,
}: IPaymentSuccessProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-40 text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-white/20 rounded-full p-3 backdrop-blur-sm">
                <CheckCircle2 className="w-20 h-20 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Payment Successful!
            </h1>
            <p className="text-green-100 text-lg">
              Your subscription has been activated
            </p>
          </div>

          <div className="p-8">
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/"
                className="flex-1 inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Go to Idea Validation
              </Link>
            </div>

            <p className="text-xs text-center text-gray-500 mt-6">
              Transaction ID: {transactionId.slice(-12)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
