"use client";
import {useEffect,useState} from "react";
import {PRODUCT_SPORTS,type ProductSport} from "../lib/clientTypes";
import Predictions from "./Predictions";
import PowerRankings from "./PowerRankings";
import Performance from "./Performance";
import MarketBoard from "./MarketBoard";

/** NBA/NFL switch shared by every section; remembered per browser. */
export default function Dashboard(){
 const [sport,setSport]=useState<ProductSport>("NBA");
 useEffect(()=>{try{const s=localStorage.getItem("rounders.sport");if(s==="NBA"||s==="NFL")setSport(s)}catch{/* default NBA */}},[]);
 const choose=(s:ProductSport)=>{setSport(s);try{localStorage.setItem("rounders.sport",s)}catch{/* not persisted */}};
 return <>
  <nav className="sportSwitch" aria-label="Sport">{PRODUCT_SPORTS.map(s=><button key={s} className={s===sport?"active":""} aria-pressed={s===sport} onClick={()=>choose(s)}>{s}</button>)}
   <a href="#predictions">Predictions</a><a href="#rankings">Power Index</a><a href="#performance">Track record</a><a href="#markets">Line shop</a></nav>
  <Predictions sport={sport}/>
  <PowerRankings sport={sport}/>
  <Performance sport={sport}/>
  <MarketBoard sport={sport}/>
 </>;
}
