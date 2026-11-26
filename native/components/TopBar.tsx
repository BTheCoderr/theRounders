"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import {initSession,isSignedIn} from "../lib/clientAuth";

/** Slim app bar; also picks up magic-link sessions and keeps them refreshed. */
export default function TopBar(){
 const [signedIn,setSignedIn]=useState(false);
 useEffect(()=>{
  const sync=()=>setSignedIn(isSignedIn());
  sync();window.addEventListener("rounders:auth",sync);
  void initSession();
  const t=setInterval(()=>void initSession(),4*60*1000);
  return()=>{window.removeEventListener("rounders:auth",sync);clearInterval(t)};
 },[]);
 return <header className="topBar">
  <Link className="brand" href="/" aria-label="The Rounders home"><span className="brandMark" aria-hidden="true">R</span><span>ROUNDERS</span></Link>
  <nav className="topNav" aria-label="Sections">
   <Link href="/#predictions">Picks</Link><Link href="/ratings/nba">Ratings</Link><Link href="/record">Record</Link><Link href="/history/nba">History</Link><Link href="/pricing">Plans</Link>
  </nav>
  <Link className="topAction" href="/account">{signedIn?"Account":"Sign in"}</Link>
 </header>;
}
