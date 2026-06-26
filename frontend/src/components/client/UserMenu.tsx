"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { signOut as NextSignOut } from "next-auth/react";
import Link from "next/link";
import { PaymentUtil } from "@/app/checkout/util";
import { useAuth } from "@/context/AuthProvider";

export default function UserMenuComponent() {
  const router = useRouter();
  const { signOut, user: AuthUser } = useAuth();

  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");

  const menuRef = useRef<HTMLDivElement>(null);

  const handleRemoveLocalStorage = () => {
    PaymentUtil.removeFromLocalStorage("tempIdea");
    PaymentUtil.removeFromLocalStorage("ideaReply");
    PaymentUtil.removeFromLocalStorage("pending_transactions");
    PaymentUtil.removeFromLocalStorage("userData");
    PaymentUtil.removeFromLocalStorage("IsConsulting");
    PaymentUtil.removeFromLocalStorage("IsConsulted");
    PaymentUtil.removeFromLocalStorage("selectedAddOns");
    signOut();
  };

  const handleLogout = async () => {
    try {
      const response = await fetch("/api/v1/auth/signout", {
        method: "DELETE",
        credentials: "include",
      });

      const data = await response.json();

      if (response.status === 401) {
        await NextSignOut({ callbackUrl: "/", redirect: false });
        setOpen(false);
        handleRemoveLocalStorage();
        setError("");
        window.location.replace("/signin");
        // await router.push('/');
        return;
      } else if (response.status > 499) {
        setError(data.message);
        return;
      }

      await NextSignOut({
        callbackUrl: `https://accounts.google.com/Logout?continue=${process.env.NEXT_PUBLIC_NEXTAUTH_URL}`,
      });
      setOpen(false);
      handleRemoveLocalStorage();
      setError("");
      await router.push("/");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div>
      {AuthUser?.email ? (
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setOpen((prev) => !prev)}
            className="px-4 py-2 text-gray-800 font-medium border border-gray-300 rounded-md hover:bg-gray-100"
          >
            {AuthUser?.email}
            {error !== "" ? (
              <div className="text-red-500 text-sm mb-4 text-center">
                {error}
              </div>
            ) : (
              ""
            )}
          </button>

          {open && (
            <div className="absolute right-0 mt-2 w-40 bg-white border rounded-md shadow-lg z-50">
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100"
              >
                Signout
              </button>
            </div>
          )}
        </div>
      ) : (
        <Link
          href="/signin"
          className="px-4 py-2 text-gray-700 font-medium border border-gray-300 rounded-md hover:bg-gray-100"
        >
          Sign In
        </Link>
      )}
    </div>
  );
}
