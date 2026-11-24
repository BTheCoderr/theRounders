"use client";
import {useEffect,useState} from "react";
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
  <a className="brand" href="/" aria-label="The Rounders home"><span className="brandMark" aria-hidden="true">R</span><span>ROUNDERS</span></a>
  <nav className="topNav" aria-label="Sections">
   <a href="/#predictions">Picks</a><a href="/ratings">Ratings</a><a href="/record">Record</a><a href="/history">History</a><a href="/pricing">Plans</a>
  </nav>
  <a className="topAction" href="/account">{signedIn?"Account":"Sign in"}</a>
 </header>;
}
