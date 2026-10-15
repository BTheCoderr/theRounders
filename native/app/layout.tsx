import "./globals.css";
import Link from "next/link";
export const metadata={title:"The Rounders",description:"Sports analytics command center"};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}<footer className="siteFooter"><span>© {new Date().getFullYear()} The Rounders · Research and paper tracking only</span><nav aria-label="Legal and support"><Link href="/support">Support</Link><Link href="/privacy">Privacy Policy</Link><a href="mailto:Bferrell514@gmail.com">Contact</a></nav></footer></body></html>}