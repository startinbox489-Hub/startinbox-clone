import { unstable_cache } from "next/cache";
import ConfigService from "../config";

export const fetchUser = unstable_cache(
  async (accessToken: string) => {
    const res = await fetch(
      `${ConfigService.get("BASE_URL")}/api/v1/auth/user/me`,
      {
        headers: { Authorization: `Bearer ${accessToken}` },
        cache: "no-store",
      },
    );
    const data = await res.json();
    return data.status === "success" ? data.data : null;
  },
  ["user-me"], // cache key
  { revalidate: 240 }, // seconds
);
