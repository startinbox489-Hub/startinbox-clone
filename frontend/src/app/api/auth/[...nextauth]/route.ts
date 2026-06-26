import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: "openid email profile", // ensures id_token is included
        },
      },
    }),
  ],
  debug: process.env.NODE_ENV === "development",
  secret: process.env.NEXTAUTH_SECRET,

  callbacks: {
    async jwt({ token, account }) {
      // Persist tokens in JWT
      if (account) {
        token.idToken = account.id_token;
        token.accessToken = account.access_token;
      }

      return token;
    },
    async session({ session, token }) {
      // Expose tokens to the client session
      session.idToken = token.idToken as string;
      session.accessToken = token.accessToken as string;
      return session;
    },
  },
  events: {
    async signOut({ token }) {
      if (token?.accessToken) {
        try {
          await fetch(
            `https://oauth2.googleapis.com/revoke?token=${token.accessToken}`,
            {
              method: "POST",
              headers: {
                "Content-type": "application/x-www-form-urlencoded",
              },
            },
          );
          console.log("Google access token revoked successfully");
        } catch (err) {
          console.error("Failed to revoke Google token:", err);
        }
      }
    },
  },
});

export { handler as GET, handler as POST };
