"use server";

import ConfigService from "@/lib/config";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const response = await fetch(
      `${await ConfigService.get("BASE_URL")}/api/v1/auth/signup`,
      {
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
        method: "POST",
        credentials: "include",
      },
    );

    if (response.status === 422) {
      const data = await response.json();
      console.log("data: ", data);
      let message: string = data.data.message;
      if (data.data?.msg.startsWith("Value error")) {
        message = data.data?.msg.substring(12);
      }
      return NextResponse.json(
        {
          message: message.replace(/_/g, " ") || data.message,
          data: data.data,
        },
        { status: response.status },
      );
    }

    if (response.status === 409) {
      const data = await response.json();
      return NextResponse.json(
        { message: data.message, status: "conflict" },
        { status: response.status },
      );
    }
    if (response.status === 417) {
      const data = await response.json();
      return NextResponse.json(
        { message: data.message },
        { status: response.status },
      );
    }
    if (response.status > 499) {
      return NextResponse.json(
        {
          message: "Internal Server Error. Contact Us with the code #su005",
          status: "error",
        },
        { status: response.status },
      );
    }

    const data = (await response.json()).data;
    return NextResponse.json({ data }, { status: response.status });
  } catch (error) {
    console.error("proxy error signin up user:", error);
    return NextResponse.json(
      { message: "Internal Server Error" },
      { status: 500 },
    );
  }
}
