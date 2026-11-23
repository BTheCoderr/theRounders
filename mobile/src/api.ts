import {displayTeam,type Quote,type Sport,validQuote} from "./markets";
export type Feed={quotes:Quote[];provider:string;live:boolean;fresh:boolean;message:string};
export const apiOrigin=(process.env.EXPO_PUBLIC_ROUNDERS_API_URL||"").trim().replace(/\/+$/,"");
export async function fetchFeed(sport:Sport):Promise<Feed>{
 if(!apiOrigin||!/^https:\/\//i.test(apiOrigin))throw new Error("No live API configured. Demo mode is available.");
 const abort=new AbortController();
 const timeout=setTimeout(()=>abort.abort(),10000);
 try{
  const response=await fetch(apiOrigin+"/api/markets?sport="+sport,{signal:abort.signal,headers:{"Accept":"application/json"}});
  if(!response.ok)throw new Error("Market API returned "+response.status);
  const data=await response.json() as {markets?:unknown[];mode?:string;provider?:string;fresh?:boolean;fallback?:boolean};
  if(!Array.isArray(data.markets))throw new Error("Invalid market feed response");
  // Hide stale live odds. Real-but-stale prices must not be relabeled simulated.
  if(data.mode==="live"&&data.fallback!==true&&data.fresh!==true){
   return {quotes:[],provider:data.provider||"Unknown provider",live:false,fresh:false,message:"Stale provider odds withheld. Refresh later or switch to demo."};
  }
  // Never let the server's label promote demo quotes into live prices.
  const sourceLive=data.mode==="live"&&data.fallback!==true;
  const quotes=data.markets.filter(validQuote).filter(q=>q.sport===sport).map(q=>({...q,state:sourceLive&&q.state==="live"?"live" as const:"simulated" as const}));
  const live=data.mode==="live"&&!data.fallback&&quotes.every(q=>q.state==="live")&&quotes.length>0;
  return {quotes,provider:data.provider||"Unknown provider",live,fresh:live&&data.fresh===true,message:live?"Provider prices":"Demo or fallback prices"};
 }finally{clearTimeout(timeout)}
}
export type PredictionView={
 eventId:string;startsAt:string;home:string;away:string;neutral:boolean;predictedAt:string;modelVersion:string;
 projectedWinner:string;homeWinProbability:number;
 projectedHome:number|null;projectedAway:number|null;projectedSpreadHome:number|null;projectedTotal:number|null;
 market:{spreadHome:number|null;total:number|null;source:string}|null;
 trainingGames:number;status:"pending"|"graded"|"void";final:{home:number;away:number}|null;locked?:string[];
};
export type Predictions={sport:Sport;model:string;modelLabel?:string;ready:boolean;reason?:string;predictions:PredictionView[]};
const okNum=(v:unknown)=>v===null||typeof v==="number"&&Number.isFinite(v);
/** Stored, immutable pregame predictions from the champion model. */
export async function fetchPredictions(sport:Sport):Promise<Predictions>{
 if(!apiOrigin||!/^https:\/\//i.test(apiOrigin))throw new Error("Rounders API is not configured");
 const abort=new AbortController();const timeout=setTimeout(()=>abort.abort(),12000);
 try{
  const r=await fetch(apiOrigin+"/api/predictions?sport="+sport,{signal:abort.signal,headers:{Accept:"application/json"}});
  const d=await r.json() as Predictions;
  if(!d||d.sport!==sport||!Array.isArray(d.predictions))throw new Error("Invalid predictions response");
  if(!d.ready)return {...d,predictions:[]};
  const valid=d.predictions.filter(p=>typeof p.eventId==="string"&&typeof p.home==="string"&&typeof p.away==="string"
   &&typeof p.homeWinProbability==="number"&&p.homeWinProbability>0&&p.homeWinProbability<1
   &&[p.projectedHome,p.projectedAway,p.projectedSpreadHome,p.projectedTotal].every(okNum));
  return {...d,predictions:valid};
 }finally{clearTimeout(timeout)}
}
export type Summary={games:number;decided:number;winnerAccuracy:number|null;brierScore:number|null;logLoss:number|null;marginMAE:number|null;totalMAE:number|null;totalGames:number;
 calibration:Array<{from:number;to:number;forecasts:number;meanForecast:number|null;observedRate:number|null}>};
export type Performance={sport:Sport;champion:string;championLabel?:string;ready:boolean;reason?:string;
 live?:Array<{model:string;label:string;champion:boolean;summary:Summary}>;
 backtest?:null|{runDay:string;evaluatedGames:number;evaluatedWeeks:number;seasons:number[];models:Array<{model:string;label:string;summary:Summary}>}};
export async function fetchPerformance(sport:Sport):Promise<Performance>{
 if(!apiOrigin||!/^https:\/\//i.test(apiOrigin))throw new Error("Rounders API is not configured");
 const abort=new AbortController();const timeout=setTimeout(()=>abort.abort(),12000);
 try{
  const r=await fetch(apiOrigin+"/api/performance?sport="+sport,{signal:abort.signal,headers:{Accept:"application/json"}});
  const d=await r.json() as Performance;
  if(!d||d.sport!==sport||typeof d.ready!=="boolean")throw new Error("Invalid performance response");
  return d;
 }finally{clearTimeout(timeout)}
}
const key=(s:string)=>s.toLowerCase().replace(/^la\s/,"los angeles ").replace(/[^a-z0-9]+/g," ").trim();
/** The stored prediction for a market row's real game, if one exists. Never computed on the fly. */
export function predictionFor(list:PredictionView[],quote:Quote):PredictionView|undefined{
 const home=key(displayTeam(quote.sport,quote.home)),away=key(displayTeam(quote.sport,quote.away));
 return list.find(p=>key(p.home)===home&&key(p.away)===away&&p.status==="pending");
}

export type AiTarget={sport:string;away:string;home:string;eventId?:string};
export type MatchupInsight={
 mode:"ai"|"model-summary";
 answer:string;
 notice:string;
 evidence:{
  sport:string;away:string;home:string;
  projectedAway:number;projectedHome:number;homeWinProbability:number;
  trainingDataState:"external"|"simulated";trainingProvider?:string;fallback?:boolean;sampleGames?:number;
  modelVersion?:string;dataSource?:string;trainingGames?:number;
 };
};
export async function fetchMatchupInsight(quote:AiTarget,question:string):Promise<MatchupInsight>{
 if(!apiOrigin||!/^https:\/\//i.test(apiOrigin))throw new Error("Rounders API is not configured");
 const away=displayTeam(quote.sport,quote.away),home=displayTeam(quote.sport,quote.home);
 const abort=new AbortController();
 const timeout=setTimeout(()=>abort.abort(),18000);
 try{
  const response=await fetch(apiOrigin+"/api/ai/matchup",{
   method:"POST",signal:abort.signal,
   headers:{"Accept":"application/json","Content-Type":"application/json"},
   body:JSON.stringify({sport:quote.sport,away,home,question:question.trim(),...(quote.eventId?{eventId:quote.eventId}:{})})
  });
  if(!response.ok)throw new Error(response.status===429?"AI analysis limit reached. Try later.":response.status===404?"No model coverage for this matchup.":"Matchup analysis returned "+response.status);
  const data=await response.json() as Partial<MatchupInsight>;
  if((data.mode!=="ai"&&data.mode!=="model-summary")||
    typeof data.answer!=="string"||data.answer.length<5||data.answer.length>1800||
    !data.evidence||data.evidence.sport!==quote.sport||
    data.evidence.away!==away||data.evidence.home!==home||
    !Number.isFinite(data.evidence.homeWinProbability)||
    !["external","simulated"].includes(data.evidence.trainingDataState))throw new Error("Invalid matchup analysis response");
  return {...data,notice:typeof data.notice==="string"?data.notice:"Model research only. Not a guarantee."} as MatchupInsight;
 }finally{clearTimeout(timeout)}
}


export type PowerRank={
 rank:number;team:string;rating:number;games:number;record:{wins:number;losses:number;ties:number};
 averageOpponentRating:number;adjustedMargin:number;recentForm:number;
};
export type PowerRankings={
 model:"rounders-power-v2-preview";sport:Sport;dataState:"external"|"simulated";
 provider:string;fallback:boolean;coverage:"substantial"|"limited";games:number;
 medianGames:number;rankings:PowerRank[];notes:string[];
 evaluation:{method:"chronological-70-30";evaluatedGames:number;modelMAE:number|null;
  homeBaselineMAE:number|null;beatsBaseline:boolean|null;warning:string};
};
export async function fetchPowerRankings(sport:Sport):Promise<PowerRankings>{
 if(!apiOrigin||!/^https:\/\//i.test(apiOrigin))throw new Error("Rounders API not configured");
 const abort=new AbortController();
 const timeout=setTimeout(()=>abort.abort(),15000);
 try{
  const response=await fetch(apiOrigin+"/api/power-rankings?sport="+encodeURIComponent(sport),{
   headers:{Accept:"application/json"},signal:abort.signal
  });
  if(!response.ok)throw new Error("Rankings API returned "+response.status);
  const data=await response.json() as PowerRankings;
  if(data.model!=="rounders-power-v2-preview"||data.sport!==sport||
    !["external","simulated"].includes(data.dataState)||
    !Array.isArray(data.rankings)||data.rankings.some(x=>
      typeof x.team!=="string"||typeof x.rank!=="number"||
      !Number.isFinite(x.rating)||!Number.isFinite(x.games))||
    !Array.isArray(data.notes))throw new Error("Invalid ranking data");
  return data;
 }finally{clearTimeout(timeout)}
}
