"use client";
import {useEffect,useState} from "react";
const endpoint=process.env.NEXT_PUBLIC_SUPABASE_URL;
const key=process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
export default function AccountAccess(){
 const [email,setEmail]=useState(""),[user,setUser]=useState(""),[notice,setNotice]=useState(""),[busy,setBusy]=useState(false);
 useEffect(()=>{
  const hash=new URLSearchParams(window.location.hash.slice(1));
  const token=hash.get("access_token");
  if(token){sessionStorage.setItem("rounders_access_token",token);history.replaceState(null,"",window.location.pathname+window.location.search)}
  const access=sessionStorage.getItem("rounders_access_token");
  if(access&&endpoint&&key)fetch(endpoint+"/auth/v1/user",{headers:{apikey:key,Authorization:"Bearer "+access}}).then(r=>r.ok?r.json():null).then(d=>{if(d?.email)setUser(d.email);else sessionStorage.removeItem("rounders_access_token")}).catch(()=>{});
 },[]);
 async function send(e:React.FormEvent){e.preventDefault();if(!endpoint||!key){setNotice("Account sign-in is not configured yet.");return}setBusy(true);setNotice("");try{
 const r=await fetch(endpoint+"/auth/v1/otp",{method:"POST",headers:{"Content-Type":"application/json",apikey:key},body:JSON.stringify({email,create_user:true,gotrue:true,options:{email_redirect_to:window.location.origin}})});
 if(!r.ok)throw new Error("Unable to send sign-in link. Check email provider and redirect settings.");
 setNotice("Check your inbox for the Rounders sign-in link.");
 }catch(err){setNotice(err instanceof Error?err.message:"Sign-in failed")}finally{setBusy(false)}}
 async function signOut(){const access=sessionStorage.getItem("rounders_access_token");if(access&&endpoint&&key)await fetch(endpoint+"/auth/v1/logout",{method:"POST",headers:{apikey:key,Authorization:"Bearer "+access}}).catch(()=>{});sessionStorage.removeItem("rounders_access_token");setUser("");setNotice("Signed out.")}
 return <section className="panel" aria-label="Rounders account"><div><p className="tag">ROUNDERS ACCOUNT</p><h2>{user?"Signed in":"Save your Rounders identity"}</h2><p className="muted">{user?"Signed in as "+user:"Email magic-link sign-in. Paper mode remains available without an account."}</p></div>{user?<button onClick={signOut}>Sign out</button>:<form onSubmit={send}><label htmlFor="rounders-email">Email</label><input id="rounders-email" type="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@example.com"/><button type="submit" disabled={busy}>{busy?"Sending…":"Email me a sign-in link"}</button></form>}{notice&&<p role="status">{notice}</p>}</section>;
}