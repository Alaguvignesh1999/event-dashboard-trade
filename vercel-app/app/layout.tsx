import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Mono } from "next/font/google";

import "@/app/globals.css";
import { SiteHeader } from "@/components/site-header";

const headingFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-heading",
});

const monoFont = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Event Comparison Dashboard",
  description: "Dark-mode event dashboard for analogues, paths, and trade ideas.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${headingFont.variable} ${monoFont.variable}`}>
        <div className="page-shell">
          <div className="page-glow page-glow-left" />
          <div className="page-glow page-glow-right" />
          <SiteHeader />
          <main className="page-main">{children}</main>
        </div>
      </body>
    </html>
  );
}
