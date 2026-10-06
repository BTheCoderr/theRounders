import {NextRequest,NextResponse} from "next/server";
import {mockProvider} from "../../../lib/providers/mock";
export async function GET(req:NextRequest){const sport=req.nextUrl.searchParams.get("sport")||"NBA";const markets=await mockProvider.getMarkets(sport);return NextResponse.json({provider:mockProvider.name,markets});}
