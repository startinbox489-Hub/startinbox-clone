import { NextRequest, NextResponse } from "next/server";
import { getJWTHeader } from "./lib/server/decodeJwt";
import { isJWT } from "class-validator";

type UserSegment = "first_visit" | "returning_user" | "frequent_visitor";

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = request.cookies.get(process.env.AUTH_COOKIE_NAME);

  if (
    pathname.startsWith("/_next/") ||
    pathname.startsWith("/api/") ||
    pathname.includes(".") // static files
  ) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/a/posts")) {
    const cookie = request.cookies.get(process.env.AUTH_COOKIE_NAME)?.value;
    if (cookie && isJWT(cookie)) {
      const decoded = await getJWTHeader(cookie);
      if (decoded.role === "regular") {
        return NextResponse.redirect(new URL("/"));
      } else {
        return NextResponse.next();
      }
    } else {
      return NextResponse.redirect(new URL("/"));
    }
  }

  if (
    ["/analysis", "/a/posts", "/checkout", "/consult", "/next-step"].includes(
      pathname,
    )
  ) {
    if (!token) {
      return NextResponse.redirect(new URL("/signin", request.url));
    }
  }

  if (pathname !== "/") {
    return NextResponse.next();
  }

  let visitCount = 1;
  let userSegment: UserSegment = "first_visit";

  const visitCookie = request.cookies.get("visit_count");

  if (visitCookie && token) {
    visitCount = parseInt(visitCookie.value) + 1;

    if (visitCount >= 5) {
      userSegment = "frequent_visitor";
    } else if (visitCount >= 2) {
      userSegment = "returning_user";
    }
  }

  // Add headers for server components
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-user-segment", userSegment);
  requestHeaders.set("x-visit-count", visitCount.toString());

  const mainResponse = NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });

  // update cookies
  mainResponse.cookies.set("visit_count", visitCount.toString(), {
    maxAge: 60 * 60 * 24 * 365, // 1 year
    path: "/",
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
  });
  mainResponse.cookies.set("user_segment", userSegment, {
    maxAge: 60 * 60 * 24 * 365,
    path: "/",
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
  });

  // Store original URL for "back to where you left" functionality
  if (!request.cookies.get("original_referrer")) {
    mainResponse.cookies.set("original_referrer", request.nextUrl.pathname, {
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: "/",
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
    });
  }

  return mainResponse;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
