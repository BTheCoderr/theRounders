"use client";
import {useEffect,useMemo,useState} from "react";
import type {PaperBet} from "../lib/contracts";
import {loadBets,loadStartingBankroll,profitFor,saveStartingBankroll,updateBet} from "../lib/paperStore";
export default function PaperBankroll(){
 const [bets,setBets]=useState<PaperBet[]>([]);
 const [start,setStart]=useState(1000);
 const sync=()=>{setBets(loadBets());setStart(loadStartingBankroll())};
 useEffect(()=>{sync();window.addEventListener("rounders:paper",sync);return()=>window.removeEventListener("rounders:paper",sync)},[]);
 const summary=useMemo(()=>{const pl=bets.reduce((sum,b)=>sum+profitFor(b),0);const exposure=bets.filter(b=>b.status==="pending").reduce((sum,b)=>sum+b.stake,0);const settled=bets.filter(b=>b.status==="won"||b.status==="lost");const wins=settled.filter(b=>b.status==="won").length;return{pl,exposure,current:start+pl,winRate:settled.length?Math.round(wins/settled.length*100):0}},[bets,start]);
 return <section className="bankroll"><div className="sectionHead"><div><p className="tag">PAPER BANKROLL</p><h2>Track the process before the money.</h2></div><label className="bankInput">Starting $<input type="number" min="1" value={start} onChange={e=>{const v=Number(e.target.value);setStart(v);saveStartingBankroll(v)}}/></label></div><div className="bankStats"><div><small>Current</small><strong>{summary.current.toFixed(2)}</strong></div><div><small>P/L</small><strong>{summary.pl.toFixed(2)}</strong></div><div><small>Open exposure</small><strong>{summary.exposure.toFixed(2)}</strong></div><div><small>Win rate</small><strong>{summary.winRate}%</strong></div></div><div className="betHistory">{bets.length===0?<p className="muted">Your paper bets will appear here.</p>:bets.slice(0,8).map(b=><div className="betRow" key={b.id}><div><strong>{b.matchup}</strong><span>{b.selection} {b.line??""} · {b.book} · {b.price>0?"+":""}{b.price}</span></div><b>{b.stake.toFixed(2)}</b><select value={b.status} onChange={e=>updateBet(b.id,e.target.value as PaperBet["status"])}><option value="pending">Pending</option><option value="won">Won</option><option value="lost">Lost</option><option value="push">Push</option></select></div>)}</div></section>
}