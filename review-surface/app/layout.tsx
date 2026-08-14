import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FAR Bank · G3 review workspace",
  description: "Local Gate G3 hands-on package for exact-version FAR review workflow evidence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
