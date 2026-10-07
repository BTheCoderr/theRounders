import {NextRequest,NextResponse} from "next/server";
import {mockProvider} from "../../../lib/providers/mock";
const STALE_MS=120000;
export async function GET(req:NextRequest){const sport=req.nextUrl.searchParams.get("sport")||"NBA";try{const markets=await mockProvider.getMarkets(sport);const newest=markets.reduce((max,q)=>Math.max(max,new Date(q.updatedAt).getTime()),0);const ageMs=newest?Date.now()-newest:Infinity;return NextResponse.json({provider:mockProvider.name,mode:mockProvider.mode,fresh:ageMs<=STALE_MS,ageMs,markets})}catch{return NextResponse.json({provider:mockProvider.name,mode:mockProvider.mode,fresh:false,ageMs:null,markets:[],error:"Market feed unavailable"},{status:503})}}
