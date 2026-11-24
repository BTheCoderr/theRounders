import {NextResponse} from "next/server";
import {isSport} from "../../../lib/sports";
import {fetchLive} from "../../../lib/results/espnSchedule";

export const dynamic="force-dynamic";
/** Live scores and game clocks (ESPN public scoreboard), shared by every visitor through a 20-second CDN cache. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 try{
  const games=await fetchLive(sport);
  return NextResponse.json({sport,at:new Date().toISOString(),games},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=20, stale-while-revalidate=10","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({sport,at:new Date().toISOString(),games:[],unavailable:true},{headers:{"Cache-Control":"public, max-age=0, s-maxage=10","Netlify-Vary":"query"}});
 }
}
