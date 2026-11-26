import {NextResponse} from "next/server";
import {MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";
import {championFor} from "../../../lib/engine/promotion";
import {marketReport} from "../../../lib/engine/clv";
import {archiveConfigured} from "../../../lib/persistence/history";
import {listGradedPredictions} from "../../../lib/persistence/predictions";
import {openCloseLines} from "../../../lib/persistence/odds";

export const dynamic="force-dynamic";
/**
 * Market comparison for the live champion's LOCKED picks: closing line value vs the captured
 * opening line, record against the closing spread, and Brier vs the market's closing probability.
 * Only games with captured lines count. Empty until odds have been captured for graded games.
 */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 if(!archiveConfigured())return NextResponse.json({sport,ready:false,reason:"Storage is not configured."},{status:503});
 try{
  const model=championFor(sport);
  const picks=await listGradedPredictions(sport,model,2000);
  const lines=await openCloseLines(sport,picks.map(p=>p.provider_event_id));
  const rows=picks.flatMap(p=>{const l=lines.get(p.provider_event_id);return l?[{projectedMargin:p.projected_margin,homeWinProbability:p.home_win_probability,
   openSpread:l.open_spread_home,closeSpread:l.close_spread_home,closeHomeProb:l.close_home_win_prob,finalHome:p.final_home,finalAway:p.final_away}]:[];});
  return NextResponse.json({sport,ready:true,model,modelLabel:MODEL_LABELS[model],gradedPicks:picks.length,report:marketReport(rows),
   notes:["Lines are The Odds API consensus captured by our scheduled job; opening = first capture, closing = last capture before start.",
    "Games without captured lines are excluded, never estimated.","Beating the closing line is evidence about price quality, not a guarantee of profit."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=900","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({sport,ready:false,reason:"Market analytics are unavailable (odds storage may not be set up yet)."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
