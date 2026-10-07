import {NextRequest,NextResponse} from "next/server";
import {mockProvider} from "../../../lib/providers/mock";
import {liveProvider} from "../../../lib/providers/live";
const STALE_MS=120000;
export async function GET(req:NextRequest){const sport=req.nextUrl.searchParams.get("sport")||"NBA";let provider=mockProvider;let fallback=true;const liveHealth=await liveProvider.health();if(liveHealth.healthy){try{await liveProvider.getMarkets(sport);provider=liveProvider;fallback=false}catch{provider=mockProvider;fallback=true}}try{const markets=await provider.getMarkets(sport);const newest=markets.reduce((max,q)=>Math.max(max,new Date(q.updatedAt).getTime()),0);const ageMs=newest?Date.now()-newest:null;return NextResponse.json({provider:provider.name,mode:provider.mode,fallback,fresh:ageMs!==null&&ageMs<=STALE_MS,ageMs,markets})}catch{return NextResponse.json({provider:provider.name,mode:provider.mode,fallback,fresh:false,ageMs:null,markets:[],error:"Market feed unavailable"},{status:503})}}
