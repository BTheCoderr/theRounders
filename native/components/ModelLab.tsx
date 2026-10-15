"use client";
import {useEffect,useState} from "react";
type Sport="NBA"|"NFL"|"NHL"|"MLB";
type Score={model:string;games:number;mae:number|null;winnerAccuracy:number|null};
type Report={ready:boolean;sport:Sport;reason?:string;run_day?:string;data_source?:string;data_state?:string;
 historical_games?:number;evaluated_games?:number;evaluated_weeks?:number;seasons?:number[];
 metrics?:Score[];warning?:string};
const titles:Record<string,string>={
 "home-baseline":"Home-only baseline",
 "massey-ridge":"Massey-style ridge",
 "elo-margin":"Elo margin",
 "rounders-power-v2":"Rounders Power Index v2"
};
export default function ModelLab(){
 const [sport,setSport]=useState<Sport>("NBA");
 const [revision,setRevision]=useState(0);
 const [data,setData]=useState<Report|null>(null);
 const [loading,setLoading]=useState(false);
 const [error,setError]=useState("");
 useEffect(()=>{
  const controller=new AbortController();
  setLoading(true);setData(null);setError("");
  void fetch("/api/model-comparison?sport="+sport,{signal:controller.signal})
   .then(async r=>{if(!r.ok)throw new Error("Model Lab is temporarily unavailable");return r.json()})
   .then((response:Report)=>{if(!controller.signal.aborted)setData(response)})
   .catch(err=>{if(!controller.signal.aborted)setError(err instanceof Error?err.message:"Unable to load scorecard")})
   .finally(()=>{if(!controller.signal.aborted)setLoading(false)});
  return()=>controller.abort();
 },[sport,revision]);
 return <section className="panel modelLab" id="model-lab">
  <div>
   <p className="tag">MODEL LAB</p>
   <h2>Can Rounders beat its benchmarks?</h2>
   <p className="muted">Weekly walk-forward evaluations pit Rounders Power Index v2 against Elo, a basic Massey-style system and a home-advantage-only baseline. Each model predicts the same held-out games.</p>
   <div className="sports">{(["NBA","NFL","NHL","MLB"] as const).map(id=><button key={id} className={id===sport?"active":""} onClick={()=>setSport(id)} aria-pressed={id===sport}>{id}</button>)}</div>
   <button className="modelLabRefresh" disabled={loading} onClick={()=>setRevision(x=>x+1)}>Refresh results</button>
   {loading?<p className="muted" role="status">Loading scorecard…</p>:null}
   {error?<p className="modelLabWarning" role="alert">{error}</p>:null}
   {data&&!data.ready?<p className="muted">{data.reason||"Waiting for first historical evaluation."}</p>:null}
   {data?.ready?<div className="modelLabResults">
    <p className="muted">{data.data_state==="simulated"?"SIMULATED HISTORY — not validated":"EXTERNAL COMPLETED GAME RESULTS"} · {data.data_source||"Unknown source"} · {data.run_day||"Unknown date"}</p>
    <p className="muted">{data.historical_games??0} archived historical games · {data.evaluated_games??0} held-out games across {data.evaluated_weeks??0} weeks · Years: {data.seasons?.join(", ")||"unavailable"}</p>
    <p className="modelLabWarning">{data.warning}</p>
    <div className="modelLabGrid">{(data.metrics||[]).map(metric=><article key={metric.model} className="modelLabMetric">
     <h3>{titles[metric.model]||metric.model}</h3>
     <strong>{metric.mae===null?"N/A":metric.mae.toFixed(2)}</strong>
     <span>Mean absolute margin error</span>
     <p>{metric.winnerAccuracy===null?"Unmeasured":metric.winnerAccuracy.toFixed(1)+"%"} winner accuracy · {metric.games} games</p>
    </article>)}</div>
   </div>:null}
   <p className="muted">Lower error is better. A single historical lead does not prove future superiority. No real-money wagering or guaranteed outcomes.</p>
  </div>
 </section>;
}
