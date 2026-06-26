"use server";

import { proxyWithAuth } from "@/lib/server/apiProxy";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const response = await proxyWithAuth(`/api/v1/payments/billing/verify`, {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });
    const data = await response.json();

    const cookies = response.headers.getSetCookie();
    const headers = new Headers();
    headers.append("Set-Cookie", cookies[0]); // access
    headers.append("Set-Cookie", cookies[1]); // refresh
    // console.log('data: ', data);

    return NextResponse.json(data, { status: response.status, headers });
  } catch (error) {
    console.error("generating verifying billing payment error:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: {}, status: "error" },
      { status: 500 },
    );
  }
}
