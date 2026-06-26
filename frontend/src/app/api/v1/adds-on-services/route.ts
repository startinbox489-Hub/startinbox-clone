import ConfigService from "@/lib/config";
import { NextResponse } from "next/server";

export async function GET(req: Request) {
  try {
    const response = await fetch(
      `${ConfigService.get("BASE_URL")}/api/v1/adds-on-services`,
      {
        headers: {
          "Content-Type": "application/json",
        },
        method: "GET",
      },
    );

    if (!response.ok) {
      return NextResponse.json(
        { message: "Failed to fetch adds-on services", data: [] },
        { status: response.status },
      );
    }

    const data = await response.json();
    console.log("adds-on services fetched successfully");
    return NextResponse.json(
      { message: "Failed to fetch adds-on services", data },
      { status: response.status },
    );
  } catch (error) {
    console.error("proxy error fetching adds-on services:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: [] },
      { status: 500 },
    );
  }
}
