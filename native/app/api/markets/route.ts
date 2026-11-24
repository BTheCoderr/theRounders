import {NextRequest,NextResponse} from "next/server";
import {liveProvider} from "../../../lib/providers/live";
const STALE_MS=120000;
import {ALL_SPORTS} from "../../../lib/sports";
const SPORTS=new Set<string>(ALL_SPORTS);
// Per-instance cache so visitors cannot drain the odds provider's quota; the CDN caches too.
const cache=new Map<string,{at:number;body:unknown}>();
const CACHE_MS=45000;
export async function GET(req:NextRequest){
 const key=(req.nextUrl.searchParams.get("sport")||"NBA").toUpperCase();
 const hit=cache.get(key);
 if(hit&&Date.now()-hit.at<CACHE_MS)return NextResponse.json(hit.body,{headers:{"Cache-Control":"public, max-age=0, s-maxage=30","Netlify-Vary":"query","X-Rounders-Cache":"hit"}});
 const res=await compute(req);
 if(res.status===200){try{cache.set(key,{at:Date.now(),body:await res.clone().json()})}catch{/* do not cache */}}
 return res;
}
async function compute(req:NextRequest){
 const sport=(req.nextUrl.searchParams.get("sport")||"NBA").toUpperCase();
 if(!SPORTS.has(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 const headers={"Cache-Control":"public, max-age=0, s-maxage=30","Netlify-Vary":"query"};
 const unavailable=()=>NextResponse.json({provider:liveProvider.name,mode:"unavailable",fallback:false,fresh:false,ageMs:null,markets:[],error:"Market feed unavailable"},{status:503,headers:{"Cache-Control":"no-store"}});
 try{
  if(!(await liveProvider.health()).healthy)return unavailable();
  const markets=(await liveProvider.getMarkets(sport)).filter(q=>q.state==="live"&&Date.parse(q.startTime)>Date.now());
  const newest=markets.reduce((max,q)=>Math.max(max,Date.parse(q.updatedAt)||0),0);
  const ageMs=newest?Date.now()-newest:null;
  return NextResponse.json({provider:liveProvider.name,mode:"live",fallback:false,fresh:ageMs!==null&&ageMs>=0&&ageMs<=STALE_MS,ageMs,markets},{headers});
 }catch{return unavailable()}
}
