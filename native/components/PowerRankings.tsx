"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import type {ProductSport} from "../lib/clientTypes";
import {nickname,onColor,team} from "../lib/teams";
const teamSlug=(n:string)=>n.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");

type Rank={rank:number;team:string;rating:number;games:number;averageOpponentRating:number;recentForm:number};
type Board={dataState:"external"|"simulated";provider:string;fallback:boolean;rankings:Rank[];notes:string[]};
export default function PowerRankings({sport}:{sport:ProductSport}){
 const [b,setB]=useState<Board|null>(null),[error,setError]=useState("");
 useEffect(()=>{
  const c=new AbortController();setB(null);setError("");
  fetch("/api/power-rankings?sport="+sport,{signal:c.signal})
   .then(async r=>{if(!r.ok)throw new Error();const x=await r.json() as Board;if(!c.signal.aborted)setB(x)})
   .catch(()=>{if(!c.signal.aborted)setError("Rankings are unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 const max=b?Math.max(1,...b.rankings.map(r=>Math.abs(r.rating))):1;
 const rows=b?b.rankings.slice(0,10):[];
 return <section className="block" id="rankings">
  <div className="blockHead"><h2>Power Index</h2>{b?.dataState==="simulated"?<span className="chip warnChip">SIMULATED</span>:null}</div>
  {error?<p className="empty">{error}</p>:!b?<div className="rankList skeleton"/>:<>
   <ol className="rankList">{rows.map(r=>{const t=team(sport,r.team);return <li key={r.team}>
    <span className="rankNo">{r.rank}</span>
    <span className="teamBadge sm" style={{background:t.color,color:onColor(t.color)}} aria-hidden="true">{t.abbr}</span>
    <Link className="rankName" href={`/teams/${sport.toLowerCase()}/${teamSlug(r.team)}`}>{nickname(r.team,sport)}</Link>
    <span className="rankBar" aria-hidden="true"><i className={r.rating>=0?"pos":"neg"} style={{width:Math.abs(r.rating)/max*50+"%"}}/></span>
    <span className={"rankVal "+(r.rating>=0?"pos":"neg")}>{r.rating>0?"+":""}{r.rating.toFixed(1)}</span>
   </li>})}</ol>
   <Link className="textButton" href={"/ratings/"+sport.toLowerCase()}>Full ratings: offense, defense, schedule →</Link>
   <p className="fine">Points better than an average team on a neutral floor, adjusted for schedule and weighted toward recent games.</p>
  </>}
 </section>;
}
