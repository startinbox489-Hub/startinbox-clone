"use server";

import ConfigService from "@/lib/config";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const response = await fetch(
      `${await ConfigService.get("BASE_URL")}/api/v1/auth/signin`,
      {
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
        method: "POST",
        credentials: "include",
      },
    );
    const data = await response.json();

    const access_token = data?.data?.token?.access_token;
    const refresh_token = response.headers.get("x-refresh-token");

    if (response.status === 422) {
      console.log("signin data: ", data);
      let message: string = data.data.message;
      if (data.data?.msg.startsWith("Value error")) {
        message = data.data?.msg.substring(12);
      }

      const nextRes = NextResponse.json(
        {
          message: message.replace(/_/g, " ") || data.message,
          data: data.data,
          user: null,
        },
        { status: response.status },
      );
      return nextRes;
    }

    if ([409, 403, 417].includes(response.status)) {
      console.log("signin data: ", data);
      return NextResponse.json(
        {
          message: data.message,
          user: null,
          status: "error",
        },
        { status: response.status },
      );
    }

    if (response.status > 499) {
      console.log("signin data: ", data);
      return NextResponse.json(
        {
          message: "Internal Server Error. Contact Us with the code #su005",
          status: "error",
          user: null,
        },
        { status: response.status },
      );
    }
    // Store tokens in httpOnly cookies
    const headers = new Headers();
    headers.append(
      "Set-Cookie",
      `access_token=${access_token}; Path=/; HttpOnly; Secure; SameSite=Lax`,
    );
    headers.append(
      "Set-Cookie",
      `refresh_token=${refresh_token}; Path=/; HttpOnly; Secure; SameSite=Lax`,
    );

    return NextResponse.json(
      { message: data.message, user: data.data.user, status: data.status },
      { status: response.status, headers },
    );
  } catch (error) {
    console.error("proxy error signin in user:", error);
    return NextResponse.json(
      { message: "Internal Server Error", user: null, status: "error" },
      { status: 500 },
    );
  }
}
