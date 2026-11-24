import "./globals.css";
import Link from "next/link";
import TopBar from "../components/TopBar";
export const metadata={title:"The Rounders · Sports ratings & predictions",description:"Ratings and pregame predictions for the NBA, NFL, college basketball, college football, NHL and MLB, with a public, graded track record."};
export const viewport={width:"device-width",initialScale:1,themeColor:"#070F1F"};
export default function RootLayout({children}:{children:React.ReactNode}){
 return <html lang="en"><body>
  <TopBar/>
  {children}
  <footer className="siteFooter"><span>© {new Date().getFullYear()} The Rounders · Research only, no wagering</span>
   <nav aria-label="Legal and support"><Link href="/pricing">Plans</Link><Link href="/support">Support</Link><Link href="/privacy">Privacy</Link><a href="mailto:Bferrell514@gmail.com">Contact</a></nav></footer>
 </body></html>;
}
