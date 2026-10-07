import "./globals.css";
export const metadata={title:"The Rounders",description:"Sports analytics command center"};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}