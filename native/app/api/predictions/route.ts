import {NextResponse} from "next/server";
import {archiveConfigured} from "../../../lib/persistence/history";
import {listUpcomingPredictions} from "../../../lib/persistence/predictions";
import {championFor} from "../../../lib/engine/promotion";
import {MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";

export const dynamic="force-dynamic";
/** Champion-model pregame predictions for upcoming NBA/NFL games, exactly as stored before each game. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"NBA and NFL only"},{status:400});
 const model=championFor(sport);
 if(!archiveConfigured())return NextResponse.json({sport,model,ready:false,predictions:[],reason:"Prediction storage is not configured."},{status:503});
 try{
  const rows=await listUpcomingPredictions(sport,model);
  return NextResponse.json({sport,model,modelLabel:MODEL_LABELS[model],ready:true,dataState:"model",
   predictions:rows.map(r=>({
    eventId:r.provider_event_id,startsAt:r.starts_at,home:r.home,away:r.away,neutral:r.neutral,
    predictedAt:r.predicted_at,modelVersion:r.model_version,totalsModel:r.totals_model,
    projectedWinner:r.projected_winner,homeWinProbability:r.home_win_probability,
    projectedHome:r.projected_home,projectedAway:r.projected_away,
    projectedSpreadHome:Number((-r.projected_margin).toFixed(1)),projectedTotal:r.projected_total,
    market:r.market_source?{spreadHome:r.market_spread_home,total:r.market_total,source:r.market_source,state:"live"}:null,
    trainingGames:r.training_games,trainingThrough:r.training_through,
    status:r.grade_status,final:r.final_home===null?null:{home:r.final_home,away:r.final_away}
   })),
   notice:"Predictions are frozen at the time shown and never edited. Win probabilities come from a fixed margin-to-probability mapping; see /api/performance for how they have actually performed."
  },{headers:{"Cache-Control":"public, max-age=0, s-maxage=120"}});
 }catch{
  return NextResponse.json({sport,model,ready:false,predictions:[],reason:"Predictions are temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
