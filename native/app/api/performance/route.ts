import {NextResponse} from "next/server";
import {archiveConfigured} from "../../../lib/persistence/history";
import {latestBacktest,listGradedPredictions,summarizeStored} from "../../../lib/persistence/predictions";
import {championFor} from "../../../lib/engine/promotion";
import {CANDIDATE_MODELS,MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";

export const dynamic="force-dynamic";
/**
 * Two kinds of evidence, never mixed:
 *  live     = predictions stored before each game and graded afterwards (the real track record)
 *  backtest = weekly walk-forward forecasts simulated on history (out-of-sample, but not recorded live)
 */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 const champion=championFor(sport);
 if(!archiveConfigured())return NextResponse.json({sport,champion,ready:false,reason:"Performance storage is not configured."},{status:503});
 try{
  const [graded,backtest]=await Promise.all([listGradedPredictions(sport,null,5000),latestBacktest(sport)]);
  const live=CANDIDATE_MODELS.map(model=>{
   const rows=graded.filter(r=>r.model_id===model);
   return {model,label:MODEL_LABELS[model],champion:model===champion,
    from:rows.length?rows[rows.length-1].starts_at:null,through:rows.length?rows[0].starts_at:null,
    summary:summarizeStored(rows)};
  });
  return NextResponse.json({sport,champion,championLabel:MODEL_LABELS[champion],ready:true,
   live,
   backtest:backtest?{runDay:backtest.run_day,engineRevision:backtest.engine_revision,dataSource:backtest.data_source,
    historicalGames:backtest.historical_games,evaluatedGames:backtest.evaluated_games,evaluatedWeeks:backtest.evaluated_weeks,
    seasons:backtest.seasons,from:backtest.from_game,through:backtest.through_game,
    models:backtest.models.map(m=>({...m,label:MODEL_LABELS[m.model]??m.model})),totals:backtest.totals,promotion:backtest.promotion}:null,
   notes:[
    "Live results count only predictions stored before the game started.",
    "Backtest results are simulated pregame forecasts on past seasons; they are out-of-sample but were not published at the time.",
    "Against-the-spread and over/under records appear only for games where a live pregame market line was captured.",
    "No result here implies future profitability."
   ]},{headers:{"Cache-Control":"public, max-age=0, s-maxage=300"}});
 }catch{
  return NextResponse.json({sport,champion,ready:false,reason:"Performance data is temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
