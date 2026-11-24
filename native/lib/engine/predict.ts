import type {CompletedGame} from "../powerRatings";
import {CANDIDATE_MODELS,ENGINE_REVISION,SPORT_SETTINGS,fitMarginModel,type EngineSport,type ModelId} from "./models.ts";
import {TOTALS_MODEL,fitTotals} from "./totals.ts";
import {buildSchedule} from "./v3.ts";
import {winProbability} from "./metrics.ts";

export type UpcomingGame={
 eventId:string;startsAt:string;season:number;
 home:string;away:string;homeId:string;awayId:string;neutral:boolean;
};
/** One immutable pregame prediction, as stored in rounders_predictions. */
export type PredictionRecord={
 sport:EngineSport;provider:"espn";provider_event_id:string;season:number;starts_at:string;
 home:string;away:string;home_team_id:string;away_team_id:string;neutral:boolean;
 model_id:ModelId;model_version:string;totals_model:string;
 predicted_at:string;
 projected_home:number;projected_away:number;projected_margin:number;projected_total:number;
 home_win_probability:number;projected_winner:string;
 training_games:number;training_through:string|null;data_source:string;
};
export const modelVersion=(m:ModelId)=>`${m}@${ENGINE_REVISION}`;
const r2=(x:number)=>Number(x.toFixed(2));

/**
 * Predict every upcoming game with every candidate model, using only games that
 * finished before `now`. Games starting within `minLeadMinutes` are skipped so a
 * stored prediction is always made before tip-off/kickoff.
 */
export function predictUpcoming(history:CompletedGame[],upcoming:UpcomingGame[],sport:EngineSport,now:Date,
 opts:{models?:readonly ModelId[];minLeadMinutes?:number;dataSource:string;sigmas?:Partial<Record<ModelId,number>>}):PredictionRecord[]{
 const models=opts.models??CANDIDATE_MODELS;
 const lead=(opts.minLeadMinutes??10)*60000;
 const past=history.filter(g=>Date.parse(g.date)<now.getTime());
 const through=past.length?past[past.length-1].date:null;
 const totals=fitTotals(past,sport,now);
 // Schedule = past game dates + the upcoming slate (dates only), for rest features.
 const schedule=buildSchedule([...past,...upcoming.map(g=>({date:g.startsAt,home:g.home,away:g.away}))]);
 const out:PredictionRecord[]=[];
 for(const m of models){
  const predict=fitMarginModel(m,past,sport,now,schedule);
  // σ calibrated from the model's out-of-sample backtest errors; documented default otherwise.
  const given=opts.sigmas?.[m];
  const sigma=typeof given==="number"&&given>0?given:SPORT_SETTINGS[sport].marginSigma;
  for(const g of upcoming){
   if(!(Date.parse(g.startsAt)-now.getTime()>=lead))continue;
   const margin=predict(g.home,g.away,g.neutral,g.startsAt),t=totals.predict(g.home,g.away,g.neutral);
   if(margin===null||!Number.isFinite(margin)||!t)continue;
   // Scores are split around the totals model so margin and total stay consistent.
   const home=(t.total+margin)/2,away=(t.total-margin)/2;
   const p=winProbability(margin,sigma);
   out.push({sport,provider:"espn",provider_event_id:g.eventId,season:g.season,starts_at:new Date(g.startsAt).toISOString(),
    home:g.home,away:g.away,home_team_id:g.homeId,away_team_id:g.awayId,neutral:g.neutral,
    model_id:m,model_version:modelVersion(m),totals_model:TOTALS_MODEL,predicted_at:now.toISOString(),
    projected_home:r2(home),projected_away:r2(away),projected_margin:r2(margin),projected_total:r2(t.total),
    home_win_probability:Number(p.toFixed(4)),projected_winner:margin>=0?g.home:g.away,
    training_games:past.length,training_through:through,data_source:opts.dataSource});
  }
 }
 return out;
}

/** Grade one prediction against a final score. */
export function gradePrediction(p:{projected_margin:number;projected_total:number;home_win_probability:number},homeScore:number,awayScore:number){
 const margin=homeScore-awayScore,decided=margin!==0;
 const y=margin>0?1:0;
 return {
  final_home:homeScore,final_away:awayScore,
  winner_correct:decided?(p.home_win_probability>=0.5)===(y===1):null,
  brier:decided?Number(((p.home_win_probability-y)**2).toFixed(5)):null,
  margin_error:Number((p.projected_margin-margin).toFixed(2)),
  total_error:Number((p.projected_total-(homeScore+awayScore)).toFixed(2))
 };
}

const HOUR=3600000,DAY=24*HOUR;
/** NBA: about one day ahead (today's slate). NFL: the coming week on Tuesdays, otherwise a two-day catch-up. */
export function snapshotWindow(sport:EngineSport,now:Date):{from:Date;to:Date}{
 const ahead=sport==="NBA"?26*HOUR:now.getUTCDay()===2?7*DAY:2*DAY;
 return {from:now,to:new Date(now.getTime()+ahead)};
}
