import {NextResponse} from "next/server";
import {archiveConfigured} from "../../../lib/persistence/history";
import {listUpcomingPredictions} from "../../../lib/persistence/predictions";
import {championFor} from "../../../lib/engine/promotion";
import {LIVE_MODELS,MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";
import {planForRequest} from "../../../lib/billing/server";
import {gatePrediction} from "../../../lib/billing/gating";
import {hasFeature} from "../../../lib/billing/plans";
import type {StoredPrediction} from "../../../lib/persistence/predictions";

export const dynamic="force-dynamic";
/** Champion-model pregame predictions for upcoming NBA/NFL games, exactly as stored before each game. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 const model=championFor(sport);
 if(!archiveConfigured())return NextResponse.json({sport,model,ready:false,predictions:[],reason:"Prediction storage is not configured."},{status:503});
 try{
  const {plan}=await planForRequest(req);
  const view=(r:StoredPrediction)=>gatePrediction({
    eventId:r.provider_event_id,startsAt:r.starts_at,home:r.home,away:r.away,neutral:r.neutral,
    predictedAt:r.predicted_at,modelVersion:r.model_version,totalsModel:r.totals_model,
    projectedWinner:r.projected_winner,homeWinProbability:r.home_win_probability,
    projectedHome:r.projected_home as number|null,projectedAway:r.projected_away as number|null,
    projectedSpreadHome:Number((-r.projected_margin).toFixed(1)) as number|null,projectedTotal:r.projected_total as number|null,
    market:r.market_source?{spreadHome:r.market_spread_home,total:r.market_total,source:r.market_source,state:"live" as const}:null,
    trainingGames:r.training_games,trainingThrough:r.training_through,
    status:r.grade_status,final:r.final_home===null?null:{home:r.final_home,away:r.final_away}
  },plan);
  const rows=await listUpcomingPredictions(sport,model);
  // Edge: every candidate model's stored prediction for the same games, labeled as challengers.
  const challengers=hasFeature(plan,"predictions.challengers")
    ?await Promise.all(LIVE_MODELS.filter(m=>m!==model).map(async m=>({model:m,label:MODEL_LABELS[m],predictions:(await listUpcomingPredictions(sport,m)).map(view)})))
    :null;
  return NextResponse.json({sport,model,modelLabel:MODEL_LABELS[model],ready:true,dataState:"model",plan,
   upgrade:plan==="free"?"/pricing":null,
   predictions:rows.map(view),challengers,
   notice:"Predictions are frozen at the time shown and never edited. Win probabilities are calibrated on each model's out-of-sample errors; see /api/performance for how they have actually performed."
  },{headers:{"Cache-Control":"private, no-store","Vary":"Authorization"}});
 }catch{
  return NextResponse.json({sport,model,ready:false,predictions:[],reason:"Predictions are temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
