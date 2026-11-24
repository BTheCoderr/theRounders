"use client";
import {useState} from "react";
import {authHeaders} from "../lib/clientAuth";

/** Starts Stripe Checkout (test mode) or opens the billing portal. */
export default function PlanButton({plan,label,portal=false}:{plan?:"pro"|"edge";label:string;portal?:boolean}){
 const [busy,setBusy]=useState(false),[msg,setMsg]=useState("");
 async function go(){
  setBusy(true);setMsg("");
  try{
   const headers=authHeaders();
   if(!headers.Authorization){setMsg("Sign in with your email link on the home page first.");return}
   const r=await fetch(portal?"/api/billing/portal":"/api/billing/checkout",{method:"POST",headers:{"Content-Type":"application/json",...headers},body:JSON.stringify(portal?{}:{plan})});
   const d=await r.json() as {url?:string;error?:string;manage?:boolean};
   if(r.ok&&d.url&&/^https:\/\/(checkout|billing)\.stripe\.com\//.test(d.url)){window.location.assign(d.url);return}
   setMsg(d.error||"Something went wrong.");
  }catch{setMsg("Billing is unavailable right now.")}finally{setBusy(false)}
 }
 return <div className="planAction"><button onClick={go} disabled={busy}>{busy?"Opening…":label}</button>{msg?<p className="warn" role="status">{msg}</p>:null}</div>;
}
