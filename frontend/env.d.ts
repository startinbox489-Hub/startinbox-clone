declare namespace NodeJS {
  interface ProcessEnv {
    NODE_ENV: "development" | "production" | "test";

    // Public
    NEXT_PUBLIC_NEXTAUTH_URL: string;
    NEXTAUTH_URL: string;

    // Private
    GOOGLE_CLIENT_ID: string;
    GOOGLE_CLIENT_SECRET: string;
    BACKEND_BASE_URL: string;
    API_BASE_URL: string;
    NEXT_PUBLIC_GA_ID: string;
    NEXT_PUBLIC_GA_PATH: string;
    NEXT_PUBLIC_META_PIXEL_ID: string;
    NEXT_PUBLIC_META_PIXEL_ID: string;
    NEXT_SERVER_ACTIONS_ENCRYPTION_KEY: string;
    AUTH_COOKIE_NAME: string;
  }
}
