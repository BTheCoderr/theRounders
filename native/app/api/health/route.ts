import {NextResponse} from "next/server";
export function GET(){return NextResponse.json({ok:true,service:"rounders-native",mode:"controlled",timestamp:new Date().toISOString()})}