"use client";
import {useEffect,useState} from "react";
import {authHeaders} from "../../lib/clientAuth";
import PlanButton from "../../components/PlanButton";
import AccountAccess from "../../components/AccountAccess";

type Account={signedIn:boolean;email?:string|null;plan:string;planName?:string;testMode?:boolean;
 subscriptions?:Array<{plan:string|null;status:string;currentPeriodEnd:string|null;cancelAtPeriodEnd:boolean}>};
export default function AccountPage(){
 const [a,setA]=useState<Account|null>(null),[error,setError]=useState(""),[checkout,setCheckout]=useState<string|null>(null);
 useEffect(()=>{
  setCheckout(new URLSearchParams(window.location.search).get("checkout"));
  const load=()=>fetch("/api/account",{headers:authHeaders(),cache:"no-store"}).then(r=>r.json()).then(setA).catch(()=>setError("Account unavailable."));
  load();window.addEventListener("rounders:auth",load);return()=>window.removeEventListener("rounders:auth",load);
 },[]);
 const sub=a?.subscriptions?.find(s=>["active","trialing","past_due"].includes(s.status));
 return <main className="accountPage">
  <section className="hero compact"><p className="eyebrow">ACCOUNT</p><h1>{a?.signedIn?"Your plan":"Sign in"}</h1></section>
  {checkout==="success"?<p className="testBanner">Payment complete. Your plan updates within a few seconds; refresh if it still shows Free.</p>:null}
  {error?<p className="warn">{error}</p>:!a?<div className="panel2 skeleton"/>:!a.signedIn?<AccountAccess/>:<>
   <section className="panel2 planSummary">
    <small>{a.email}</small>
    <h2>{a.planName}</h2>
    {sub?<p className="muted">{sub.status==="past_due"?"Payment failed, update your card":sub.cancelAtPeriodEnd?"Cancels":"Renews"} {sub.currentPeriodEnd?new Date(sub.currentPeriodEnd).toLocaleDateString([], {month:"short",day:"numeric",year:"numeric"}):""}</p>:<p className="muted">Free plan</p>}
    {a.plan==="free"?<a className="btn" href="/pricing">See plans</a>:<PlanButton portal label="Manage billing"/>}
   </section>
   {a.plan!=="free"?<section className="panel2"><h3>Exports</h3><p className="muted">Every graded prediction as a spreadsheet.</p>
    <div className="btnRow"><button className="btn ghost" onClick={()=>void download("NBA")}>NBA CSV</button><button className="btn ghost" onClick={()=>void download("NFL")}>NFL CSV</button></div></section>:null}
   <AccountAccess/>
   {a.testMode?<p className="fine center">Billing is in Stripe test mode.</p>:null}
  </>}
 </main>;
}
async function download(sport:string){
 const r=await fetch("/api/predictions/export?sport="+sport,{headers:authHeaders()});
 if(!r.ok){alert("Export unavailable.");return}
 const url=URL.createObjectURL(await r.blob());
 const el=document.createElement("a");el.href=url;el.download=`rounders-${sport.toLowerCase()}-predictions.csv`;el.click();URL.revokeObjectURL(url);
}
