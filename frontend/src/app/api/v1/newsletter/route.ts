"use server";

import ConfigService from "@/lib/config";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const response = await fetch(
      `${await ConfigService.get("BASE_URL")}/api/v1/news-letter`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    );
    const data = await response.json();
    // console.log('server newsletter data: ', data);

    if (response.status === 409) {
      // This email is already subscribed to the newsletter
      return NextResponse.json(
        {
          message:
            "Email is already subscribed to the newsletter. Thanks again.",
          status: "conflict",
        },
        { status: response.status },
      );
    }
    if (response.status === 422) {
      return NextResponse.json(
        {
          message: data?.data?.ctx?.reason || "Invalid email address",
          status: "validation error",
        },
        { status: response.status },
      );
    }
    if (response.status > 499) {
      return NextResponse.json(
        {
          message: "Internal Server Error. Please contact us with code #nl002",
          status: "error",
        },
        { status: response.status },
      );
    }
    return NextResponse.json(
      {
        message: "Thank you for subscribing to our News Letter.",
        status: "error",
      },
      { status: response.status },
    );
  } catch (error) {
    console.error("proxy error subscribing to newsletter: ", error);
    return NextResponse.json(
      {
        message: "Internal Server Error. Please contact us with code #nl002",
        status: "error",
      },
      { status: 500 },
    );
  }
}

export async function PATCH(req: Request) {
  try {
    const body = await req.json();
    const response = await fetch(
      `${await ConfigService.get("BASE_URL")}/api/v1/news-letter`,
      {
        method: "PATCH",
        body: JSON.stringify(body),
      },
    );

    if (response.status === 404) {
      // This email is not yet subscribed to the newsletter
      return NextResponse.json(
        {
          message:
            "Email is already unsubscribed or not subscribed to our Newsletter",
          status: "error",
        },
        { status: response.status },
      );
    }
    if (response.status > 499) {
      return NextResponse.json(
        {
          message:
            "Internal Server Error. Please contact us with code #nl002.1",
          status: "error",
        },
        { status: response.status },
      );
    }
    return NextResponse.json(
      {
        message: "Email is unsubscribed from our News Letter.",
        status: "success",
      },
      { status: response.status },
    );
  } catch (error) {
    console.error("proxy error unsubscribing to newsletter: ", error);
    return NextResponse.json(
      {
        message: "Internal Server Error. Please contact us with code #nl002.1",
        status: "success",
      },
      { status: 500 },
    );
  }
}
