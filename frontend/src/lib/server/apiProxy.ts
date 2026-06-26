import { cookies } from "next/headers";

import ConfigService from "../config";

export async function proxyWithAuth(
  path: string,
  init?: RequestInit,
): Promise<Response> {
  const cookieStore = cookies();

  const accessToken = (await cookieStore).get("access_token")?.value;
  const refreshToken = (await cookieStore).get("refresh_token")?.value;

  const response = await fetch(
    `${await ConfigService.get("BASE_URL")}${path}`,
    {
      ...init,
      headers: {
        ...(init?.headers || {}),
        Authorization: accessToken ? `Bearer ${accessToken}` : "",
      },
      credentials: "include",
    },
  );

  // If access token expired → try refresh
  if (response.status === 401 && refreshToken) {
    const refreshRes = await fetch(
      `${await ConfigService.get("BASE_URL")}/api/v1/auth/refresh-tokens`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-REFRESH-TOKEN": refreshToken,
        },
      },
    );

    if (refreshRes.ok) {
      const { access_token: newAccess } = await refreshRes.json();
      const newRefreshToken = response.headers.get("x-refresh-token");

      // Create a new Headers object and append the new cookies
      const newHeaders = new Headers(refreshRes.headers);
      newHeaders.append(
        "Set-Cookie",
        `access_token=${newAccess}; Path=/; HttpOnly; Secure; SameSite=Lax`,
      );
      if (newRefreshToken) {
        newHeaders.append(
          "Set-Cookie",
          `refresh_token=${newRefreshToken}; Path=/; HttpOnly; Secure; SameSite=Lax`,
        );
      }

      // Retry original request with new token
      const origiResponse = await fetch(
        `${await ConfigService.get("BASE_URL")}${path}`,
        {
          ...init,
          headers: {
            ...(init?.headers || {}),
            Authorization: `Bearer ${newAccess}`,
          },
        },
      );
      const origBody = await origiResponse.json();

      return new Response(origBody, {
        status: origiResponse.status,
        statusText: origiResponse.statusText,
        headers: origiResponse.headers,
      });
    } else {
      (await cookieStore).delete("access_token");
      (await cookieStore).delete("refresh_token");
      // refresh token invalid → clear cookies
      const newHeaders = new Headers(response.headers);
      newHeaders.append(
        "Set-Cookie",
        `access_token=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`,
      );
      newHeaders.append(
        "Set-Cookie",
        `refresh_token=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`,
      );

      // Return a new Response object with cleared cookies
      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: newHeaders,
      });
    }
  }
  if (path.endsWith("signout")) {
    (await cookieStore).delete("access_token");
    (await cookieStore).delete("refresh_token");
    // signout → clear cookies
    const newHeaders = new Headers(response.headers);
    // Return a new Response object with cleared cookies
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  }

  return response;
}
