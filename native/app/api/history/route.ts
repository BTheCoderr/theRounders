import {NextResponse} from "next/server";
import {isSport,seasonEndDate} from "../../../lib/sports";
import {archiveConfigured,availableSeasons,getSeasonGames} from "../../../lib/persistence/history";
import {uniqueCompletedGames} from "../../../lib/powerRatings";
import {buildRatingsTable} from "../../../lib/engine/ratingsTable";

export const dynamic="force-dynamic";
/** Final regular-season Power Index ratings for any archived season. */
export async function GET(req:Request){
 const url=new URL(req.url),sport=(url.searchParams.get("sport")||"NBA").toUpperCase();
 if(!isSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 if(!archiveConfigured())return NextResponse.json({ready:false,reason:"Storage is not configured."},{status:503});
 try{
  const seasons=await availableSeasons(sport);
  if(!seasons.length)return NextResponse.json({ready:false,sport,seasons,reason:"History for this sport is still loading."});
  const asked=Number(url.searchParams.get("season"));
  // Default to the latest completed season.
  const finished=seasons.filter(y=>seasonEndDate(sport,y).getTime()<Date.now());
  const season=seasons.includes(asked)?asked:(finished[0]??seasons[0]);
  const rows=await getSeasonGames(sport,season);
  const games=uniqueCompletedGames(rows,new Date());
  if(games.length<20)return NextResponse.json({ready:false,sport,season,seasons,reason:"Not enough games archived for this season yet."});
  const end=new Date(Date.parse(games[games.length-1].date)+86400000);
  const table=buildRatingsTable(games,sport,end);
  return NextResponse.json({...table,rows:table.rows.map(r=>({...r,change:null})),ready:true,seasons,historical:true,
   notes:["Final regular-season Power Index ratings, computed from that season's results only. Team names as they were at the time."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=3600, stale-while-revalidate=600"}});
 }catch{
  return NextResponse.json({ready:false,sport,reason:"History is temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
