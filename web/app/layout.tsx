import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "The Rounders",
  description: "Sports market intelligence, line shopping, and paper bankroll tracking.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
