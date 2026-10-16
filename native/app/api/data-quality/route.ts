import {NextResponse} from "next/server";
import {getTrainingGames} from "../../../lib/persistence/history";
import {auditGameHistory} from "../../../lib/researchDataQuality";
import type {Sport} from "../../../lib/powerRatings";

export const dynamic="force-dynamic";
export async function GET(request:Request){
 const sport=(new URL(request.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!["NBA","NFL","NHL","MLB"].includes(sport))
  return NextResponse.json({error:"Unsupported sport"},{status:400});
 try{
  const data=await getTrainingGames(sport as Sport);
  const audit=auditGameHistory(data.games,sport as Sport,data.provider,data.source);
  return NextResponse.json({...audit,notice:"Approximate audit only. Not a league-certified game inventory."},{
   headers:{"Cache-Control":"public, max-age=0, s-maxage=600"}
  });
 }catch{
  return NextResponse.json({error:"Archive quality check unavailable"},{status:503,
   headers:{"Cache-Control":"no-store"}});
 }
}
