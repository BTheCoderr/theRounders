"use client";
import {useEffect,useState} from "react";
import {PLANS,type PlanId} from "../lib/billing/plans";
import {authHeaders} from "../lib/clientAuth";
import PlanButton from "./PlanButton";

const ORDER:PlanId[]=["free","pro","edge"];
/** Plan cards that know the visitor's current plan: no checkout for someone who already pays. */
export default function PlanCards(){
 const [current,setCurrent]=useState<PlanId|null>(null),[signedIn,setSignedIn]=useState(false);
 useEffect(()=>{
  fetch("/api/account",{headers:authHeaders(),cache:"no-store"}).then(r=>r.json())
   .then((a:{signedIn:boolean;plan:PlanId})=>{setSignedIn(a.signedIn);setCurrent(a.plan)}).catch(()=>setCurrent("free"));
 },[]);
 const paid=current==="pro"||current==="edge";
 return <div className="planGrid">{ORDER.map(id=>{const p=PLANS[id];const mine=current===id&&(signedIn||id==="free");
  return <article key={id} className={"planCard"+(id==="pro"?" featured":"")+(mine?" current":"")}>
   <div className="planTop"><p className="tag">{p.name.toUpperCase()}</p>{mine?<span className="chip liveChip">YOUR PLAN</span>:id==="pro"?<span className="chip">MOST POPULAR</span>:null}</div>
   <h2>{p.monthlyUsd?`$${p.monthlyUsd.toFixed(2)}`:"$0"}<small>{p.monthlyUsd?" / month":" forever"}</small></h2>
   <ul>{p.pitch.map(x=><li key={x}>{x}</li>)}</ul>
   {id==="free"?(paid?<span className="planNote">Included in your plan</span>:<a className="btn ghost" href="/">Use for free</a>)
    :mine?<PlanButton portal label="Manage your plan"/>
    :paid?<PlanButton portal label={id==="edge"?"Upgrade to Edge":"Switch to Pro"}/>
    :<PlanButton plan={id} label={"Get "+p.name}/>}
  </article>})}</div>;
}
