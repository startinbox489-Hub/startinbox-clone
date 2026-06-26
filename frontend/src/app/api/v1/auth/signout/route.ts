"use server";

import { proxyWithAuth } from "@/lib/server/apiProxy";
import { NextResponse } from "next/server";

export async function DELETE(_: Request) {
  try {
    const response = await proxyWithAuth("/api/v1/auth/signout", {
      method: "DELETE",
    });
    const data = await response.json();
    const cookies = response.headers.getSetCookie();
    const headers = new Headers();
    headers.append("Set-Cookie", cookies[0]);
    headers.append("Set-Cookie", cookies[1]);

    if (!response.ok) {
      return NextResponse.json(
        { status: "error", message: "Logout failed" },
        { status: response.status, headers },
      );
    }

    return NextResponse.json(
      { message: "Logged out successfully", ...data },
      { headers, status: response.status },
    );
  } catch (error) {
    console.error("Logout failed:", error);
    return NextResponse.json(
      { status: "error", message: "Logout failed" },
      { status: 500 },
    );
  }
}
