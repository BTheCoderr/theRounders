import "./globals.css";
import Link from "next/link";
import TopBar from "../components/TopBar";
import type {Metadata} from "next";
const SITE_TITLE="The Rounders · Sports ratings & predictions";
const SITE_DESCRIPTION="Ratings and pregame predictions for the NBA, NFL, college basketball, college football, NHL and MLB, with a public, graded track record.";
// Absolute URLs for social cards: Netlify sets URL to the production origin at build time.
const SITE_URL=process.env.URL||process.env.NEXT_PUBLIC_SITE_URL||"https://therounders.netlify.app";
export const metadata:Metadata={
 metadataBase:new URL(SITE_URL),
 title:SITE_TITLE,
 description:SITE_DESCRIPTION,
 applicationName:"The Rounders",
 alternates:{canonical:"/"},
 openGraph:{type:"website",siteName:"The Rounders",locale:"en_US",url:"/",title:SITE_TITLE,description:SITE_DESCRIPTION},
 twitter:{card:"summary_large_image",title:SITE_TITLE,description:SITE_DESCRIPTION}
};
export const viewport={width:"device-width",initialScale:1,themeColor:"#070F1F"};
export default function RootLayout({children}:{children:React.ReactNode}){
 return <html lang="en"><body>
  <TopBar/>
  {children}
  <footer className="siteFooter"><span>© {new Date().getFullYear()} The Rounders · Research only, no wagering</span>
   <nav aria-label="Legal and support"><Link href="/pricing">Plans</Link><Link href="/support">Support</Link><Link href="/privacy">Privacy</Link><Link href="/methodology">Methodology</Link><Link href="/faq">FAQ</Link><Link href="/terms">Terms</Link><a href="mailto:Bferrell514@gmail.com">Contact</a></nav></footer>
 </body></html>;
}
