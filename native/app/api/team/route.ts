import {NextResponse} from "next/server";
import {isEngineSport} from "../../../lib/engine/models";
import {loadTeam} from "../../../lib/persistence/pageData";

export const dynamic="force-dynamic";
/**
 * One team: ratings row, weekly rating history, this season's results with the
 * pick we stored before each game, and upcoming games (winner + probability only,
 * the free tier; spreads and totals stay on the plan-gated predictions API).
 */
export async function GET(req:Request){
 const url=new URL(req.url);
 const sport=(url.searchParams.get("sport")||"").toUpperCase(),slug=(url.searchParams.get("team")||"").toLowerCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Valid sport and team are required"},{status:400});
 const data=await loadTeam(sport,slug);
 if(!data.ready){const {status,...body}=data;return NextResponse.json(body,{status,headers:{"Cache-Control":"no-store"}});}
 return NextResponse.json(data,{headers:{"Cache-Control":"public, max-age=0, s-maxage=900, stale-while-revalidate=300","Netlify-Vary":"query"}});
}
