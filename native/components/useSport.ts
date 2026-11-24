"use client";
import {useEffect,useState} from "react";
import type {ProductSport} from "../lib/clientTypes";

/** NBA/NFL choice shared across pages (URL ?sport= wins, then the remembered choice). */
export function useSport():[ProductSport,(s:ProductSport)=>void]{
 const [sport,setSport]=useState<ProductSport>("NBA");
 useEffect(()=>{
  let s:string|null=null;
  try{s=new URLSearchParams(location.search).get("sport")?.toUpperCase()??null;if(s!=="NBA"&&s!=="NFL")s=localStorage.getItem("rounders.sport");}catch{/* default */}
  if(s==="NBA"||s==="NFL")setSport(s);
 },[]);
 const choose=(s:ProductSport)=>{setSport(s);try{localStorage.setItem("rounders.sport",s);history.replaceState(null,"","?sport="+s)}catch{/* not persisted */}};
 return [sport,choose];
}
