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
export type Rating={
 model:string;trainingDataState:string;trainingProvider?:string;fallback?:boolean;
 projection?:{
  projectedAway:number;projectedHome:number;fairSpreadHome:number;
  homeWinProbability:number;confidence:number;away:string;home:string;
 };
};
export async function fetchRating(quote:Quote):Promise<Rating>{
 if(!apiOrigin||!/^https:\/\//i.test(apiOrigin))throw new Error("Rating API is not configured");
 const away=displayTeam(quote.sport,quote.away),home=displayTeam(quote.sport,quote.home);
 const url=apiOrigin+"/api/ratings?sport="+encodeURIComponent(quote.sport)+"&away="+encodeURIComponent(away)+"&home="+encodeURIComponent(home);
 const abort=new AbortController();
 const timeout=setTimeout(()=>abort.abort(),10000);
 try{
  const result=await fetch(url,{signal:abort.signal,headers:{"Accept":"application/json"}});
  if(!result.ok)throw new Error("No model coverage for this matchup");
  const rating=await result.json() as Rating;
  const p=rating?.projection;
  if(!p||typeof p.away!=="string"||typeof p.home!=="string"||
     ![p.projectedAway,p.projectedHome,p.fairSpreadHome,p.homeWinProbability,p.confidence].every(v=>typeof v==="number"&&Number.isFinite(v))||
     p.homeWinProbability<0||p.homeWinProbability>100||p.confidence<0||p.confidence>100){
   throw new Error("Model API returned an invalid matchup projection");
  }
  return rating;
 }finally{clearTimeout(timeout)}
}


export type MatchupInsight={
 mode:"ai"|"model-summary";
 answer:string;
 notice:string;
 evidence:{
  sport:string;away:string;home:string;
  projectedAway:number;projectedHome:number;homeWinProbability:number;
  trainingDataState:"external"|"simulated";trainingProvider:string;fallback:boolean;sampleGames:number;
 };
};
export async function fetchMatchupInsight(quote:Quote,question:string):Promise<MatchupInsight>{
 if(!apiOrigin||!/^https:\/\//i.test(apiOrigin))throw new Error("Rounders API is not configured");
 const away=displayTeam(quote.sport,quote.away),home=displayTeam(quote.sport,quote.home);
 const abort=new AbortController();
 const timeout=setTimeout(()=>abort.abort(),18000);
 try{
  const response=await fetch(apiOrigin+"/api/ai/matchup",{
   method:"POST",signal:abort.signal,
   headers:{"Accept":"application/json","Content-Type":"application/json"},
   body:JSON.stringify({sport:quote.sport,away,home,question:question.trim()})
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
