import {NextResponse} from "next/server";
import {mockProvider} from "../../../lib/providers/mock";
export async function GET(){const provider=await mockProvider.health();return NextResponse.json({ok:provider.healthy,service:"rounders-native",provider,timestamp:new Date().toISOString()})}