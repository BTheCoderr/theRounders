"use client";
import {useEffect,useState} from "react";
import {sendMagicLink,signOut,signedInEmail} from "../lib/clientAuth";

/** Email magic-link sign-in, or the signed-in identity with a sign-out button. */
export default function AccountAccess(){
 const [email,setEmail]=useState(""),[user,setUser]=useState<string|null>(null),[notice,setNotice]=useState(""),[busy,setBusy]=useState(false);
 useEffect(()=>{const sync=()=>setUser(signedInEmail());sync();window.addEventListener("rounders:auth",sync);return()=>window.removeEventListener("rounders:auth",sync)},[]);
 async function send(e:React.FormEvent){e.preventDefault();setBusy(true);setNotice("");
  try{await sendMagicLink(email);setNotice("Check your inbox for the sign-in link.")}
  catch(err){setNotice(err instanceof Error?err.message:"Sign-in failed")}finally{setBusy(false)}}
 if(user)return <section className="panel2 row"><span className="muted">Signed in as {user}</span><button className="btn ghost" onClick={()=>void signOut()}>Sign out</button></section>;
 return <section className="panel2" aria-label="Sign in">
  <h3>Sign in with your email</h3>
  <p className="muted">We&apos;ll email you a one-tap link. No password.</p>
  <form className="signin" onSubmit={send}>
   <input id="rounders-email" type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com" aria-label="Email"/>
   <button className="btn" type="submit" disabled={busy}>{busy?"Sending…":"Send link"}</button>
  </form>
  {notice&&<p role="status" className="notice">{notice}</p>}
 </section>;
}
