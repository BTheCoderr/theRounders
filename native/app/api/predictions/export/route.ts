import {NextResponse} from "next/server";
import {planForRequest} from "../../../../lib/billing/server";
import {hasFeature} from "../../../../lib/billing/plans";
import {listGradedPredictions} from "../../../../lib/persistence/predictions";
import {championFor} from "../../../../lib/engine/promotion";
import {isEngineSport} from "../../../../lib/engine/models";
import {toCsv} from "../../../../lib/billing/csv";

export const dynamic="force-dynamic";
/** CSV of graded predictions (Pro: live model; Edge: every candidate model). */
export async function GET(req:Request){
 const {plan}=await planForRequest(req);
 if(!hasFeature(plan,"export.history"))return NextResponse.json({error:"CSV export is part of Rounders Pro.",upgrade:"/pricing"},{status:402});
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 const model=hasFeature(plan,"predictions.challengers")?null:championFor(sport);
 const rows=await listGradedPredictions(sport,model,5000);
 const csv=toCsv(["sport","event_id","starts_at","away","home","model_version","predicted_at","projected_winner","home_win_probability",
  "projected_away","projected_home","projected_spread_home","projected_total","market_spread_home","market_total","final_away","final_home","winner_correct","brier","margin_error","total_error"],
  rows.map(r=>[r.sport,r.provider_event_id,r.starts_at,r.away,r.home,r.model_version,r.predicted_at,r.projected_winner,r.home_win_probability,
   r.projected_away,r.projected_home,-r.projected_margin,r.projected_total,r.market_spread_home,r.market_total,r.final_away,r.final_home,r.winner_correct,r.brier,r.margin_error,r.total_error]));
 return new NextResponse(csv,{headers:{"Content-Type":"text/csv; charset=utf-8","Content-Disposition":`attachment; filename="rounders-${sport.toLowerCase()}-predictions.csv"`,"Cache-Control":"private, no-store"}});
}
