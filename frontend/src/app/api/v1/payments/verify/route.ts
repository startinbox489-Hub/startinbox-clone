"use server";

import { proxyWithAuth } from "@/lib/server/apiProxy";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const response = await proxyWithAuth("/api/v1/payments/verify", {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    });
    const data = await response.json();
    const cookies = response.headers.getSetCookie();
    // console.log('cookies: ', cookies);
    const headers = new Headers();
    headers.append("Set-Cookie", cookies[0]); // access
    headers.append("Set-Cookie", cookies[1]); // refresh
    console.log("data: ", data);

    return NextResponse.json(
      {
        ...data,
        ...(response.status === 401 && { status: "signin required" }),
      },
      { headers, status: response.status },
    );
  } catch (error) {
    console.error("Payment verification proxy error:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: null, status: "error" },
      { status: 500 },
    );
  }
}
