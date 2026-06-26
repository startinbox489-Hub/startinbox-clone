type StatusCaseProps = {
  status:
    | "loading"
    | "success"
    | "failed"
    | "pending"
    | "notfound"
    | "signin"
    | "amount"
    | "cancelled";
  title: string;
  message: string;
  action?: React.ReactNode;
};

const statusConfig = {
  loading: {
    color: "text-blue-500",
    icon: (
      <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-500"></div>
    ),
  },
  success: {
    color: "text-green-500",
    icon: (
      <svg
        className="w-20 h-20 text-green-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  failed: {
    color: "text-red-500",
    icon: (
      <svg
        className="w-20 h-20 text-red-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    ),
  },
  cancelled: {
    color: "text-red-500",
    icon: (
      <svg
        className="w-20 h-20 text-red-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    ),
  },
  pending: {
    color: "text-yellow-500",
    icon: (
      <svg
        className="w-20 h-20 text-yellow-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  notfound: {
    color: "text-gray-500",
    icon: (
      <svg
        className="w-20 h-20 text-gray-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  signin: {
    color: "text-indigo-500",
    icon: (
      <svg
        className="w-20 h-20 text-indigo-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M5.121 17.804A9 9 0 1112 21a9 9 0 01-6.879-3.196z"
        />
      </svg>
    ),
  },
  amount: {
    color: "text-orange-500",
    icon: (
      <svg
        className="w-20 h-20 text-orange-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M12 8c-1.5 0-3 .5-3 2s1.5 2 3 2 3 .5 3 2-1.5 2-3 2"
        />
      </svg>
    ),
  },
};

export default function StatusCase({
  status,
  title,
  message,
  action,
}: StatusCaseProps) {
  const { icon, color } = statusConfig[status];

  return (
    <div className="flex flex-col items-center justify-center space-y-4 text-center">
      {icon}
      <h2 className={`text-2xl font-bold ${color}`}>{title}</h2>
      <p className="text-lg text-gray-700">{message}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
