import {NextResponse} from "next/server";
import {readComparison} from "../../../lib/persistence/history";
import type {Sport} from "../../../lib/powerRatings";

export const dynamic="force-dynamic";
export async function GET(request:Request){
 const sport=(new URL(request.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!["NBA","NFL","NHL","MLB"].includes(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 try{
  const report=await readComparison(sport as Sport);
  if(!report)return NextResponse.json({ready:false,reason:"No completed historical evaluation has been stored yet.",sport},
   {headers:{"Cache-Control":"no-store"}});
  return NextResponse.json({ready:true,...report,disclaimer:"Research-grade comparison in progress. No independently verified superiority or betting guarantee."},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=300"}});
 }catch{
  return NextResponse.json({ready:false,error:"Historical model scorecard unavailable",sport},
   {status:503,headers:{"Cache-Control":"no-store"}});
 }
}
