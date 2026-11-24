import {NextResponse} from "next/server";
import {isEngineSport} from "../../../lib/engine/models";
import {buildRatingsTable} from "../../../lib/engine/ratingsTable";
import {verifiedHistory} from "../../../lib/persistence/ratingsData";
import {archiveConfigured} from "../../../lib/persistence/history";

export const dynamic="force-dynamic";
/** Full NBA/NFL ratings table: rating, offense, defense, schedule strength, record and movement. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"NBA and NFL only"},{status:400});
 if(!archiveConfigured())return NextResponse.json({sport,ready:false,reason:"Ratings storage is not configured."},{status:503});
 try{
  const now=new Date();
  const {provider,games}=await verifiedHistory(sport,now);
  if(games.length<50)return NextResponse.json({sport,ready:false,reason:"Not enough verified games yet."},{status:503});
  const table=buildRatingsTable(games,sport,now);
  return NextResponse.json({...table,ready:true,provider,model:"power-v2",
   notes:["Rounders Power Index ratings from verified regular-season results. These are not Kenneth Massey's ratings.",
    "Offense and defense are points per game better than average against an average opponent."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=900, stale-while-revalidate=300"}});
 }catch{
  return NextResponse.json({sport,ready:false,reason:"Ratings are temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
