"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import {authHeaders} from "../../lib/clientAuth";
import PlanButton from "../../components/PlanButton";

type Account={signedIn:boolean;email?:string|null;plan:string;planName?:string;testMode?:boolean;
 subscriptions?:Array<{plan:string|null;status:string;currentPeriodEnd:string|null;cancelAtPeriodEnd:boolean}>};
export default function AccountPage(){
 const [a,setA]=useState<Account|null>(null),[error,setError]=useState("");
 const [checkout,setCheckout]=useState<string|null>(null);
 useEffect(()=>{
  setCheckout(new URLSearchParams(window.location.search).get("checkout"));
  fetch("/api/account",{headers:authHeaders(),cache:"no-store"}).then(r=>r.json()).then(setA).catch(()=>setError("Account unavailable."));
 },[]);
 return <main className="pricingPage">
  <Link className="policyBack" href="/">← Back to predictions</Link>
  <p className="eyebrow">ACCOUNT</p><h1>Your plan.</h1>
  {checkout==="success"?<p className="testBanner">Checkout complete. Your plan updates as soon as Stripe confirms it (usually a few seconds); refresh if it still shows Free.</p>:null}
  {error?<p className="warn">{error}</p>:!a?<p className="muted">Loading…</p>:!a.signedIn?<p className="muted">Sign in with your email link on the <Link href="/">home page</Link> to see your plan.</p>:<section className="panel stack">
   <p className="muted">Signed in as {a.email}</p>
   <h2>{a.planName}</h2>
   {a.subscriptions?.map((s,i)=><p key={i} className="muted small">{s.plan??"unknown plan"} · {s.status}{s.currentPeriodEnd?` · ${s.cancelAtPeriodEnd?"ends":"renews"} ${new Date(s.currentPeriodEnd).toLocaleDateString()}`:""}</p>)}
   {a.plan==="free"?<Link className="navAction" href="/pricing">See plans</Link>:<PlanButton portal label="Manage billing, change plan or cancel"/>}
   {a.plan!=="free"?<p className="muted small">Exports: <a href="#" onClick={e=>{e.preventDefault();void download("NBA")}}>NBA CSV</a> · <a href="#" onClick={e=>{e.preventDefault();void download("NFL")}}>NFL CSV</a></p>:null}
   {a.testMode?<p className="muted small">Billing is in Stripe test mode.</p>:null}
  </section>}
 </main>;
}
async function download(sport:string){
 const r=await fetch("/api/predictions/export?sport="+sport,{headers:authHeaders()});
 if(!r.ok){alert("Export unavailable.");return}
 const url=URL.createObjectURL(await r.blob());
 const a=document.createElement("a");a.href=url;a.download=`rounders-${sport.toLowerCase()}-predictions.csv`;a.click();URL.revokeObjectURL(url);
}
