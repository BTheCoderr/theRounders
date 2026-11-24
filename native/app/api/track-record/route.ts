import {NextResponse} from "next/server";
import {MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";
import {championFor} from "../../../lib/engine/promotion";
import {listGradedPredictions,summarizeStored} from "../../../lib/persistence/predictions";
import {archiveConfigured} from "../../../lib/persistence/history";

export const dynamic="force-dynamic";
/** Public ledger: every graded pick the live model stored before its game, newest first. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 if(!archiveConfigured())return NextResponse.json({sport,ready:false,reason:"Storage is not configured."},{status:503});
 try{
  const model=championFor(sport);
  const rows=await listGradedPredictions(sport,model,1000);
  return NextResponse.json({sport,ready:true,model,modelLabel:MODEL_LABELS[model],summary:summarizeStored(rows),
   picks:rows.slice(0,400).map(r=>({eventId:r.provider_event_id,startsAt:r.starts_at,predictedAt:r.predicted_at,home:r.home,away:r.away,
    winner:r.projected_winner,probability:r.projected_winner===r.home?r.home_win_probability:1-r.home_win_probability,
    projectedSpreadHome:Number((-r.projected_margin).toFixed(1)),projectedTotal:r.projected_total,
    final:{home:r.final_home,away:r.final_away},correct:r.winner_correct,marginError:r.margin_error,modelVersion:r.model_version})),
   notes:["Each pick was stored before its game started and is never edited. Spreads and totals are shown after the final only.",
    "Ties are excluded from accuracy. No result here implies future profitability."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=300","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({sport,ready:false,reason:"Track record is temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
