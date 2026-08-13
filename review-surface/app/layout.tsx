import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FAR Bank · Exact-version review",
  description: "Local internal review surface for auditable FAR question candidates.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
