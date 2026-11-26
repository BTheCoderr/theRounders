import {NextResponse} from "next/server";
import {MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";
import {championFor} from "../../../lib/engine/promotion";
import {EDGE_POINTS,EDGE_PROB,edgePick,edgeRecord,type EdgePick} from "../../../lib/engine/edge";
import {archiveConfigured} from "../../../lib/persistence/history";
import {listGradedPredictions,listUpcomingPredictions,type StoredPrediction} from "../../../lib/persistence/predictions";
import {latestLines} from "../../../lib/persistence/odds";

export const dynamic="force-dynamic";
/**
 * Edge picks for the live champion: locked picks whose line differs from the market by a
 * pre-declared threshold. Finished games are graded against the last line captured before
 * start (the close); upcoming games show the current captured line.
 */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 if(!archiveConfigured())return NextResponse.json({sport,ready:false,reason:"Storage is not configured."},{status:503});
 try{
  const model=championFor(sport),now=Date.now();
  const [upcoming,graded]=await Promise.all([listUpcomingPredictions(sport,model),listGradedPredictions(sport,model,1000)]);
  const rows=[...upcoming.filter(p=>p.grade_status==="pending"&&Date.parse(p.starts_at)>now),...graded];
  const lines=await latestLines(sport,rows.map(p=>p.provider_event_id));
  const pick=(p:StoredPrediction)=>{const l=lines.get(p.provider_event_id);return l?edgePick({sport,eventId:p.provider_event_id,startsAt:p.starts_at,home:p.home,away:p.away,
   projectedMargin:p.projected_margin,homeWinProbability:p.home_win_probability,
   marketSpreadHome:l.spread_home===null?null:Number(l.spread_home),marketHomeProb:l.home_win_prob===null?null:Number(l.home_win_prob),
   lineSource:l.provider==="espn"?"DraftKings via ESPN":"Sportsbook consensus",lineAt:l.captured_at,
   finalHome:p.final_home,finalAway:p.final_away}):null;};
  const open=rows.filter(p=>p.grade_status==="pending").map(pick).filter((x):x is EdgePick=>x!==null);
  const done=graded.map(pick).filter((x):x is EdgePick=>x!==null);
  const linedGames=graded.filter(p=>lines.has(p.provider_event_id)).length;
  return NextResponse.json({sport,ready:true,model,modelLabel:MODEL_LABELS[model],
   threshold:EDGE_POINTS[sport]!==undefined?{kind:"points",value:EDGE_POINTS[sport]}:{kind:"probability",value:EDGE_PROB[sport]},
   upcoming:open,record:edgeRecord(done),recent:done.slice(0,100),gradedWithLine:linedGames,
   notes:["An edge pick is a locked pick whose line differs from the market by at least the threshold, which was fixed in advance.",
    "Finished games are graded against the last line captured before start. Spread picks need 52.4% to break even at -110.",
    "Small samples are noise. No result here implies future profitability."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=300","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({sport,ready:false,reason:"Edge picks are temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
