import {NextRequest,NextResponse} from "next/server";
import {mockProvider} from "../../../lib/providers/mock";
import {liveProvider} from "../../../lib/providers/live";
const STALE_MS=120000;
const SPORTS=new Set(["NBA","NFL","NHL","MLB"]);
// Per-instance cache so visitors cannot drain the odds provider's quota; the CDN caches too.
const cache=new Map<string,{at:number;body:unknown}>();
const CACHE_MS=45000;
export async function GET(req:NextRequest){
 const key=(req.nextUrl.searchParams.get("sport")||"NBA").toUpperCase();
 const hit=cache.get(key);
 if(hit&&Date.now()-hit.at<CACHE_MS)return NextResponse.json(hit.body,{headers:{"Cache-Control":"public, max-age=0, s-maxage=30","X-Rounders-Cache":"hit"}});
 const res=await compute(req);
 if(res.status===200){try{cache.set(key,{at:Date.now(),body:await res.clone().json()})}catch{/* do not cache */}}
 return res;
}
async function compute(req:NextRequest){const sport=(req.nextUrl.searchParams.get("sport")||"NBA").toUpperCase();if(!SPORTS.has(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});let providerName=mockProvider.name,mode=mockProvider.mode,fallback=true;try{const health=await liveProvider.health();let markets=await mockProvider.getMarkets(sport);if(health.healthy){try{const live=await liveProvider.getMarkets(sport);if(live.length){markets=live;providerName=liveProvider.name;mode=liveProvider.mode;fallback=false}}catch{fallback=true}}const newest=markets.reduce((max,q)=>Math.max(max,new Date(q.updatedAt).getTime()),0);const ageMs=newest?Date.now()-newest:null;return NextResponse.json({provider:providerName,mode,fallback,fresh:mode==="live"&&ageMs!==null&&ageMs>=0&&ageMs<=STALE_MS,ageMs,markets},{headers:{"Cache-Control":"public, max-age=0, s-maxage=30"}})}catch{return NextResponse.json({provider:providerName,mode,fallback,fresh:false,ageMs:null,markets:[],error:"Market feed unavailable"},{status:503})}}
