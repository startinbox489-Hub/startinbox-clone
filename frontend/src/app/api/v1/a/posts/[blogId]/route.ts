"use server";

import { proxyWithAuth } from "@/lib/server/apiProxy";
import { NextResponse } from "next/server";

export async function GET(
  req: Request,
  { params }: { params: Promise<{ blogId: string }> },
) {
  try {
    const { blogId } = await params;

    const response = await proxyWithAuth(`/api/v1/a/posts/${blogId}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });

    const cookies = response.headers.getSetCookie();
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
    console.error("blog id proxy error:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: {} },
      { status: 500 },
    );
  }
}

export async function DELETE(
  req: Request,
  { params }: { params: Promise<{ blogId: string }> },
) {
  try {
    const { blogId } = await params;

    const response = await proxyWithAuth(`/api/v1/a/posts/${blogId}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    });

    const cookies = response.headers.getSetCookie();
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
    console.error("blog id proxy error:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: {} },
      { status: 500 },
    );
  }
}

export async function PUT(
  req: Request,
  { params }: { params: Promise<{ blogId: string }> },
) {
  try {
    console.log("putting...");
    const { blogId } = await params;
    const body = await req.json();
    const response = await proxyWithAuth(`/api/v1/a/posts/${blogId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(body),
    });

    const cookies = response.headers.getSetCookie();
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
    console.error("blog update proxy error:", error);
    return NextResponse.json(
      { message: "Internal Server Error", data: {} },
      { status: 500 },
    );
  }
}
