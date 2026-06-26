import ConfigService from "@/lib/config";
import { NextResponse } from "next/server";

export async function GET(req: Request) {
  try {
    const response = await fetch(
      `${await ConfigService.get("BASE_URL")}/api/v1/subscription-plans`,
      {
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    if (!response.ok) {
      return NextResponse.json(
        { message: "Failed to fetch plans API", data: [] },
        { status: response.status },
      );
    }

    const data = await response.json();
    console.log("plans fetched successfully");
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("proxy error fetching plans:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: [] },
      { status: 500 },
    );
  }
}
