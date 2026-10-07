import {NextResponse} from "next/server";
import type {ProjectionSnapshot} from "../../../lib/performance";
import {listSnapshots,persistenceConfigured,putSnapshot} from "../../../lib/persistence/supabase";
export const dynamic="force-dynamic";
export async function GET(){if(!persistenceConfigured())return NextResponse.json({configured:false,snapshots:[]});try{return NextResponse.json({configured:true,snapshots:await listSnapshots()})}catch(error){return NextResponse.json({configured:true,error:error instanceof Error?error.message:"Persistence failure",snapshots:[]},{status:503})}}
export async function POST(req:Request){if(!persistenceConfigured())return NextResponse.json({error:"Central persistence is not configured"},{status:503});const s=await req.json() as ProjectionSnapshot;if(!s.id||!s.eventId||!s.modelVersion||!Number.isFinite(s.homeWinProbability))return NextResponse.json({error:"Invalid projection snapshot"},{status:400});try{await putSnapshot(s);return NextResponse.json({ok:true},{status:201})}catch(error){return NextResponse.json({error:error instanceof Error?error.message:"Persistence failure"},{status:503})}}
