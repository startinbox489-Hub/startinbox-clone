import { getRandomColor } from "@/lib/client/getRandomColor";
import ConfigService from "@/lib/config";
import { proxyWithAuth } from "@/lib/server/apiProxy";
import { NextResponse } from "next/server";

export async function GET(req: Request) {
  try {
    const response = await fetch(
      `${await ConfigService.get("BASE_URL")}/api/v1/testimonials`,
      {
        headers: {
          "Content-Type": "application/json",
        },
        next: { revalidate: 3600 }, // every 1 hour
      },
    );

    if (!response.ok) {
      return NextResponse.json(
        { message: "Failed to fetch testimonials", data: [] },
        { status: response.status },
      );
    }

    const data = await response.json();

    return NextResponse.json(
      {
        message: data.message,
        status: data.status,
        data: data.data.map(
          (testimonial: {
            id: string;
            testimonial: string;
            firstname: string;
            lastname: string;
            image_url: string;
            rating: number;
          }) => {
            return { ...testimonial, color: getRandomColor() };
          },
        ),
      },
      { status: response.status },
    );
  } catch (error) {
    console.error("proxy error fetching testimonials:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: [] },
      { status: 500 },
    );
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const response = await proxyWithAuth("/api/v1/testimonials", {
      method: "POST",
      body: JSON.stringify(body),
      headers: { "Content-Type": "application/json" },
    });
    const cookies = response.headers.getSetCookie();
    console.log("cookies: ", cookies);
    const headers = new Headers();
    headers.append("Set-Cookie", cookies[0]); // access
    headers.append("Set-Cookie", cookies[1]); // refresh
    const data = await response.json();

    return NextResponse.json(
      {
        ...data,
        ...(response.status === 401 && { status: "signin required" }),
      },
      { headers, status: response.status },
    );
  } catch (error) {
    console.error("proxy error sending review:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: {} },
      { status: 500 },
    );
  }
}
