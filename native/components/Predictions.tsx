"use client";
import {SLATE,SPORT_LABEL,OFFSEASON} from "../lib/clientTypes";
import {useEffect,useState} from "react";
import {kickoff,signed,type PredictionView,type PredictionsResponse,type ProductSport} from "../lib/clientTypes";
import {authHeaders} from "../lib/clientAuth";
import {nickname,onColor,team} from "../lib/teams";

type Insight={mode:"ai"|"model-summary";answer:string;notice:string};
function Badge({sport,name}:{sport:string;name:string}){
 const t=team(sport,name);
 return <span className="teamBadge" style={{background:t.color,color:onColor(t.color)}} aria-hidden="true">{t.abbr}</span>;
}
function Explain({sport,p,onClose}:{sport:ProductSport;p:PredictionView;onClose:()=>void}){
 const [q,setQ]=useState("Why does the model lean this way, and what could it be missing?");
 const [busy,setBusy]=useState(false),[result,setResult]=useState<Insight|null>(null),[error,setError]=useState("");
 async function ask(){
  setBusy(true);setError("");setResult(null);
  try{
   const r=await fetch("/api/ai/matchup",{method:"POST",headers:{"Content-Type":"application/json",...authHeaders()},
    body:JSON.stringify({sport,away:p.away,home:p.home,question:q,eventId:p.eventId})});
   const d=await r.json();
   if(!r.ok)throw new Error(d.error||"Analysis unavailable");
   setResult(d as Insight);
  }catch(e){setError(e instanceof Error?e.message:"Analysis unavailable")}finally{setBusy(false)}
 }
 return <div className="explain">
  <div className="explainRow"><input aria-label="Question about this matchup" value={q} maxLength={240} onChange={e=>setQ(e.target.value)}/>
   <button disabled={busy||q.trim().length<3} onClick={ask}>{busy?"…":"Ask"}</button></div>
  {error&&<p className="warn" role="alert">{error}</p>}
  {result&&<div className="insight"><span className="chip">{result.mode==="ai"?"AI ANALYSIS":"MODEL SUMMARY"}</span><p>{result.answer}</p><small>{result.notice}</small></div>}
  <button className="textButton" onClick={onClose}>Close</button>
 </div>;
}
function Row({sport,name,score,win,final,isFinal}:{sport:string;name:string;score:number|null;win:boolean;final?:number;isFinal:boolean}){
 return <div className={"teamRow"+(win?" fav":"")}>
  <Badge sport={sport} name={name}/>
  <span className="teamName"><b>{nickname(name,sport)}</b><small>{nickname(name,sport)===name?"":name.replace(" "+nickname(name,sport),"")}</small></span>
  <span className="teamScore">{isFinal&&final!==undefined?final:score===null?"":Math.round(score)}</span>
 </div>;
}
type Live={eventId:string;state:"pre"|"in"|"post";detail:string;homeScore:number|null;awayScore:number|null};
function GameCard({sport,p,live}:{sport:ProductSport;p:PredictionView;live?:Live}){
 const [explain,setExplain]=useState(false);
 const homeFav=p.projectedWinner===p.home;
 const favP=homeFav?p.homeWinProbability:1-p.homeWinProbability;
 const locked=new Set(p.locked||[]);
 // Live scoreboard fills the gap until the official grade lands (every 15 minutes).
 const liveFinal=!p.final&&live?.state==="post"&&live.homeScore!==null&&live.awayScore!==null?{home:live.homeScore,away:live.awayScore!}:null;
 const final=p.final??liveFinal;
 const graded=(p.status==="graded"||Boolean(liveFinal))&&final;
 const inPlay=!graded&&live?.state==="in"&&live.homeScore!==null&&live.awayScore!==null;
 const correct=graded?((final!.home>final!.away)===homeFav):null;
 const hs=live?.homeScore??0,as=live?.awayScore??0;
 const leading=inPlay?(hs===as?null:(hs>as)===homeFav):null;
 const spread=p.projectedSpreadHome;
 const favLine=spread===null?null:homeFav?spread:-spread;
 return <article className="gameCard2">
  <header className="cardHead">
   <span>{graded?"Final":inPlay?<b className="liveTag">LIVE · {live!.detail}</b>:kickoff(p.startsAt)}</span>
   {inPlay?<span className={"result "+(leading===null?"":leading?"hit":"miss")}>{leading===null?"Tied":leading?"Pick leading":"Pick trailing"}</span>:graded?<span className={"result "+(correct?"hit":"miss")}>{correct?"✓ Correct":"✗ Missed"}</span>:p.status==="void"?<span className="result">Void</span>:<span className="lockTag" title={"Locked "+new Date(p.predictedAt).toLocaleString()}>Locked</span>}
  </header>
  <Row sport={sport} name={p.away} score={p.projectedAway} win={!homeFav} final={inPlay?as:final?.away} isFinal={Boolean(graded)||Boolean(inPlay)}/>
  <Row sport={sport} name={p.home} score={p.projectedHome} win={homeFav} final={inPlay?hs:final?.home} isFinal={Boolean(graded)||Boolean(inPlay)}/>
  <div className="probRow" aria-label={`${p.projectedWinner} ${Math.round(favP*100)} percent`}>
   <div className="probTrack"><i style={{width:(1-p.homeWinProbability)*100+"%",background:team(sport,p.away).color}}/><i style={{width:p.homeWinProbability*100+"%",background:team(sport,p.home).color}}/></div>
   <div className="probLabels"><span>{Math.round((1-p.homeWinProbability)*100)}%</span><span>{Math.round(p.homeWinProbability*100)}%</span></div>
  </div>
  <div className="lines">
   <div><small>Spread</small><b>{favLine===null?(locked.has("spread")?<a href="/pricing" className="proTag">PRO</a>:"—"):`${team(sport,p.projectedWinner).abbr} ${favLine>0?"+":""}${favLine.toFixed(1)}`}</b></div>
   <div><small>Total</small><b>{p.projectedTotal===null?(locked.has("total")?<a href="/pricing" className="proTag">PRO</a>:"—"):p.projectedTotal.toFixed(1)}</b></div>
   <div><small>Market</small><b>{p.market?`${p.market.spreadHome===null?"—":signed(p.market.spreadHome)} / ${p.market.total??"—"}`:locked.has("market")?<a href="/pricing" className="proTag">EDGE</a>:"—"}</b></div>
  </div>
  {p.status==="pending"&&!inPlay&&!graded?(explain?<Explain sport={sport} p={p} onClose={()=>setExplain(false)}/>:<button className="textButton" onClick={()=>setExplain(true)}>Why this pick? ›</button>):null}
 </article>;
}
export default function Predictions({sport}:{sport:ProductSport}){
 const [data,setData]=useState<PredictionsResponse|null>(null),[error,setError]=useState("");
 useEffect(()=>{
  const c=new AbortController();setData(null);setError("");
  fetch("/api/predictions?sport="+sport,{signal:c.signal,headers:authHeaders(),cache:"no-store"})
   .then(async r=>{const d=await r.json() as PredictionsResponse;if(!c.signal.aborted)setData(d)})
   .catch(()=>{if(!c.signal.aborted)setError("Predictions are unavailable right now.")});
  return()=>c.abort();
 },[sport]);
 // Poll live scores every 30s while a locked game is about to start, in progress, or awaiting its grade.
 const [live,setLive]=useState<Map<string,Live>>(new Map());
 useEffect(()=>{
  setLive(new Map());
  const now=Date.now();
  const active=(data?.predictions||[]).some(p=>p.status==="pending"&&Date.parse(p.startsAt)<now+30*60000&&Date.parse(p.startsAt)>now-8*3600000);
  if(!active)return;
  let stop=false;
  const tick=async()=>{
   if(document.visibilityState!=="visible")return;
   try{const r=await fetch("/api/live?sport="+sport);const j=await r.json() as {games:Live[]};if(!stop)setLive(new Map(j.games.map(g=>[g.eventId,g])));}catch{/* keep last */}
  };
  void tick();
  const t=setInterval(()=>void tick(),30000);
  return()=>{stop=true;clearInterval(t)};
 },[data,sport]);
 const locked=data?.predictions.some(p=>p.locked?.includes("spread"));
 return <section className="block" id="predictions">
  <div className="blockHead"><h2>{SLATE[sport]==="daily"?"Today's slate":"This week"}</h2>
   {data?.modelLabel?<span className="chip">{data.modelLabel}</span>:null}</div>
  {error?<p className="empty">{error}</p>:!data?<div className="pickGrid">{[0,1,2].map(i=><div key={i} className="gameCard2 skeleton"/>)}</div>:
   !data.ready?<p className="empty">{data.reason||"Predictions are not available yet."}</p>:
   data.predictions.length===0?<p className="empty">No {SPORT_LABEL[sport]} games locked yet. {SLATE[sport]==="weekly"?"The week's slate locks on Tuesday morning.":OFFSEASON[sport]?OFFSEASON[sport]:"Picks lock up to a day before each game, checked every hour."}</p>:
   <div className="pickGrid">{data.predictions.map(p=><GameCard key={p.eventId} sport={sport} p={p} live={live.get(p.eventId)}/>)}</div>}
  {locked?<a className="upsell" href="/pricing"><b>See every spread, total and projected score</b><span>Rounders Pro · $19.99/mo ›</span></a>:null}
  <p className="fine">Projections are locked before each game and never edited. Win probabilities are model estimates; see the track record below for how they have held up.</p>
 </section>;
}
