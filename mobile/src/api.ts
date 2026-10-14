import {type Quote,type Sport,validQuote} from "./markets";
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
  // Never let the server's label promote demo quotes into live prices.
  const quotes=data.markets.filter(validQuote).map(q=>({...q,state:data.mode==="live"&&q.state==="live"?"live" as const:"simulated" as const}));
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
 const url=apiOrigin+"/api/ratings?sport="+encodeURIComponent(quote.sport)+"&away="+encodeURIComponent(quote.away)+"&home="+encodeURIComponent(quote.home);
 const abort=new AbortController();
 const timeout=setTimeout(()=>abort.abort(),10000);
 try{
  const result=await fetch(url,{signal:abort.signal,headers:{"Accept":"application/json"}});
  if(!result.ok)throw new Error("No model coverage for this matchup");
  return await result.json() as Rating;
 }finally{clearTimeout(timeout)}
}
