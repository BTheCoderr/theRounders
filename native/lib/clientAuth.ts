"use client";
/**
 * Supabase magic-link session kept in localStorage and refreshed before it
 * expires (access tokens last one hour), so members stay signed in.
 */
const KEY="rounders.session.v1";
const endpoint=process.env.NEXT_PUBLIC_SUPABASE_URL;
const apikey=process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
type Session={access_token:string;refresh_token:string;expires_at:number;email?:string};
function read():Session|null{try{const s=JSON.parse(localStorage.getItem(KEY)||"null");return s&&s.access_token?s:null}catch{return null}}
function write(s:Session|null){try{if(s)localStorage.setItem(KEY,JSON.stringify(s));else localStorage.removeItem(KEY);sessionStorage.removeItem("rounders_access_token")}catch{/* private mode */}
 window.dispatchEvent(new Event("rounders:auth"))}
export function authHeaders():Record<string,string>{const s=read();return s?{Authorization:"Bearer "+s.access_token}:{}}
export function signedInEmail():string|null{return read()?.email??null}
export function isSignedIn():boolean{return Boolean(read())}
/** Picks up #access_token from a magic link, then refreshes an expiring session. Call once per page load. */
export async function initSession():Promise<void>{
 const hash=new URLSearchParams(window.location.hash.slice(1));
 if(hash.get("access_token")){
  const s:Session={access_token:hash.get("access_token")!,refresh_token:hash.get("refresh_token")||"",
   expires_at:Number(hash.get("expires_at"))||Math.floor(Date.now()/1000)+Number(hash.get("expires_in")||3600)};
  history.replaceState(null,"",window.location.pathname+window.location.search);
  write(s);
 }
 const s=read();if(!s||!endpoint||!apikey)return;
 if(!s.email){
  const r=await fetch(endpoint+"/auth/v1/user",{headers:{apikey,Authorization:"Bearer "+s.access_token}}).catch(()=>null);
  if(r?.ok){const u=await r.json();write({...s,email:u.email})}
 }
 if(s.expires_at-Date.now()/1000>300)return;
 if(!s.refresh_token){write(null);return}
 const r=await fetch(endpoint+"/auth/v1/token?grant_type=refresh_token",{method:"POST",headers:{apikey,"Content-Type":"application/json"},body:JSON.stringify({refresh_token:s.refresh_token})}).catch(()=>null);
 if(!r?.ok){write(null);return}
 const n=await r.json();
 write({access_token:n.access_token,refresh_token:n.refresh_token,expires_at:n.expires_at||Math.floor(Date.now()/1000)+(n.expires_in||3600),email:n.user?.email||s.email});
}
export async function sendMagicLink(email:string){
 if(!endpoint||!apikey)throw new Error("Sign-in is not configured yet.");
 const r=await fetch(endpoint+"/auth/v1/otp",{method:"POST",headers:{"Content-Type":"application/json",apikey},
  body:JSON.stringify({email,create_user:true,options:{email_redirect_to:window.location.origin+"/account"}})});
 if(!r.ok)throw new Error("Couldn't send the sign-in link. Try again in a minute.");
}
export async function signOut(){
 const s=read();
 if(s&&endpoint&&apikey)await fetch(endpoint+"/auth/v1/logout",{method:"POST",headers:{apikey,Authorization:"Bearer "+s.access_token}}).catch(()=>{});
 write(null);
}
