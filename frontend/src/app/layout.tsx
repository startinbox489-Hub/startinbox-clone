import type { Metadata } from "next";
import "./globals.css";
import { Inter } from "next/font/google";
import Footer from "@/components/server/Footer";
import Header from "@/components/client/Header/Header";
import { footerData } from "@/staticData/footerData";

import { Providers } from "@/components/client/shared/Providers";
import CookieNotice from "@/components/client/CookieNotice";
import MetaPixel from "@/components/client/MetaPixel";
import MetaPageView from "@/components/client/MetaPageView";
import Script from "next/script";
import GoogleAnalytics from "@/components/client/GoogleAnalytics";
import { AuthProvider } from "@/context/AuthProvider";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "StartInbox",
  description:
    "Validate your business idea fast before building. Test demand, get insights, and launch smarter.",
  other: {
    "facebook-domain-verification": "6az0o3yclmn00xyldhnfvgo5jk8uor",
  },
};

const inter = Inter({ subsets: ["latin"] });
export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-scroll-behavior="smooth">
      <head>
        {/* Google Analytics */}
        <Script
          strategy="afterInteractive"
          src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
        />

        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){window.dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}', {
              page_path: window.location.pathname,
            });
          `}
        </Script>
      </head>
      <body className={inter.className}>
        <AuthProvider>
          <Header />
          <main className="pt-20">
            <CookieNotice />
            <MetaPixel />
            <MetaPageView />
            <GoogleAnalytics />

            <Providers>{children}</Providers>
          </main>
          <Footer
            quickLinks={footerData.quickLinks}
            companyLinks={footerData.companyLinks}
            contactEmail={footerData.contactEmail}
            twitterHandle={footerData.twitterHandle}
            instagramHandle={footerData.instagramHandle}
            facebookHandle={footerData.facebookHandle}
            linkedInHandle={footerData.linkedInHandle}
          />
          <Toaster
            position="top-right"
            reverseOrder={true}
            gutter={8}
            toastOptions={{
              duration: 5000,
              style: {
                background: "#363636",
                color: "#fff",
              },
              success: {
                duration: 3000,
              },
            }}
          />
        </AuthProvider>
      </body>
    </html>
  );
}
