"use client";
import {useEffect,useState} from "react";
import {isProductSport,type ProductSport} from "../lib/clientTypes";

/** NBA/NFL choice shared across pages (URL ?sport= wins, then the remembered choice). */
export function useSport():[ProductSport,(s:ProductSport)=>void]{
 const [sport,setSport]=useState<ProductSport>("NBA");
 useEffect(()=>{
  let s:string|null=null;
  try{s=new URLSearchParams(location.search).get("sport")?.toUpperCase()??null;if(!isProductSport(s))s=localStorage.getItem("rounders.sport");}catch{/* default */}
  if(isProductSport(s))setSport(s);
 },[]);
 const choose=(s:ProductSport)=>{setSport(s);try{localStorage.setItem("rounders.sport",s);history.replaceState(null,"","?sport="+s)}catch{/* not persisted */}};
 return [sport,choose];
}
