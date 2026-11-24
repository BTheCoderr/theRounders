import {uniqueCompletedGames} from "../powerRatings";
import {archiveConfigured,getVerifiedResearchGames,readTeamRegistry,rest} from "./history";
import {fetchFinals,fetchUpcoming} from "../results/espnSchedule";
import {predictUpcoming,gradePrediction,snapshotWindow,type PredictionRecord,type UpcomingGame} from "../engine/predict";
import {runBacktest} from "../engine/backtest";
import {evaluatePromotion,championFor} from "../engine/promotion";
import {CANDIDATE_MODELS,ENGINE_REVISION,ENGINE_SPORTS,type EngineSport,type ModelId} from "../engine/models";
import {SPORT_CONFIG} from "../sports";
import {consensusLine} from "../engine/market";
import {liveProvider} from "../providers/live";
import {summarizeForecasts,type ForecastSummary} from "../engine/metrics";
import {sigmaFromSummary} from "../engine/calibration";
import type {MarketQuote} from "../contracts";

const HOUR=3600000,DAY=24*HOUR;

/** Create first (immutable) pregame predictions for upcoming games. Existing rows are left untouched. */
export async function snapshotPredictions(sport:EngineSport,now=new Date()){
 if(!archiveConfigured())throw new Error("Prediction storage is not configured");
 const {from,to}=snapshotWindow(sport,now);
 const [archive,registry,schedule,backtest]=await Promise.all([
  getVerifiedResearchGames(sport),readTeamRegistry(sport),fetchUpcoming(sport,from,to),latestBacktest(sport).catch(()=>null)
 ]);
 // Per-model σ from the latest out-of-sample backtest (stored σ, else its margin RMSE).
 const sigmas:Partial<Record<ModelId,number>>={};
 for(const m of backtest?.models||[])sigmas[m.model]=typeof m.sigma==="number"&&m.sigma>0?m.sigma:sigmaFromSummary(sport,m.summary);
 // Use the archive's canonical names (by provider team ID) so models recognize every club.
 const upcoming:UpcomingGame[]=schedule.map(g=>({...g,home:registry.get(g.homeId)||g.home,away:registry.get(g.awayId)||g.away}));
 const history=uniqueCompletedGames(archive.games,now);
 const rows=predictUpcoming(history,upcoming,sport,now,{dataSource:archive.provider,sigmas});
 // Attach a consensus market line only when the odds provider is genuinely live.
 let quotes:MarketQuote[]=[];
 try{if((await liveProvider.health()).healthy)quotes=await liveProvider.getMarkets(sport);}catch{quotes=[];}
 // One first prediction per game and model, even across engine revisions.
 const ids=[...new Set(rows.map(r=>r.provider_event_id))].filter(x=>/^\d+$/.test(x));
 const taken=new Set<string>();
 for(let i=0;i<ids.length;i+=100){
  const r=await rest("rounders_predictions?select=provider_event_id,model_id&sport=eq."+sport+"&provider_event_id=in.("+ids.slice(i,i+100).join(",")+")");
  for(const x of await r.json() as Array<{provider_event_id:string;model_id:string}>)taken.add(x.provider_event_id+"|"+x.model_id);
 }
 const fresh=rows.filter(r=>!taken.has(r.provider_event_id+"|"+r.model_id));
 const withMarket=fresh.map(r=>{
  const line=quotes.length?consensusLine(quotes,r.home,r.away):null;
  return {...r,market_spread_home:line?.spreadHome??null,market_total:line?.total??null,
   market_source:line&&line.books>0&&(line.spreadHome!==null||line.total!==null)?`the-odds-api consensus (${line.books} books)`:null};
 });
 for(let i=0;i<withMarket.length;i+=200){
  await rest("rounders_predictions?on_conflict=sport,provider,provider_event_id,model_version",{
   method:"POST",headers:{Prefer:"resolution=ignore-duplicates,return=minimal"},body:JSON.stringify(withMarket.slice(i,i+200))
  });
 }
 return {games:upcoming.length,predictions:withMarket.length,withMarket:withMarket.filter(r=>r.market_source).length};
}

type PendingRow={id:number;sport:EngineSport;provider_event_id:string;starts_at:string;home_team_id:string;away_team_id:string;
 projected_margin:number;projected_total:number;home_win_probability:number};
/** Grade finished games from the verified archive, then directly from the scoreboard. Bounded per run. */
export async function gradePendingPredictions(now=new Date(),limit=300){
 if(!archiveConfigured())throw new Error("Prediction storage is not configured");
 const cutoff=new Date(now.getTime()-3*HOUR).toISOString();
 const res=await rest("rounders_predictions?select=id,sport,provider_event_id,starts_at,home_team_id,away_team_id,projected_margin,projected_total,home_win_probability"+
  "&grade_status=eq.pending&starts_at=lt."+encodeURIComponent(cutoff)+"&order=starts_at.asc&limit="+limit);
 const pending=await res.json() as PendingRow[];
 if(!Array.isArray(pending)||!pending.length)return {graded:0,voided:0,pending:0};
 const finals=new Map<string,{homeId:string;awayId:string;homeScore:number;awayScore:number}>();
 const ids=[...new Set(pending.map(p=>p.provider_event_id))].filter(x=>/^\d+$/.test(x));
 for(let i=0;i<ids.length;i+=100){
  const r=await rest("rounders_games?select=provider_event_id,home_team_id,away_team_id,home_score,away_score&season_phase=eq.regular&provider_event_id=in.("+ids.slice(i,i+100).join(",")+")");
  for(const g of await r.json() as Array<{provider_event_id:string;home_team_id:string;away_team_id:string;home_score:number;away_score:number}>)
   finals.set(g.provider_event_id,{homeId:g.home_team_id,awayId:g.away_team_id,homeScore:g.home_score,awayScore:g.away_score});
 }
 for(const sport of ENGINE_SPORTS){
  const missing=pending.filter(p=>p.sport===sport&&!finals.has(p.provider_event_id));
  if(!missing.length)continue;
  const times=missing.map(p=>Date.parse(p.starts_at));
  const start=new Date(Math.max(Math.min(...times),now.getTime()-14*DAY)-DAY),end=new Date(Math.max(...times)+DAY);
  try{for(const [id,f] of await fetchFinals(sport,start,end))if(!finals.has(id))finals.set(id,f);}catch{/* retry next run */}
 }
 let graded=0,voided=0;
 for(const p of pending){
  const f=finals.get(p.provider_event_id);
  let patch:Record<string,unknown>|null=null;
  if(f&&f.homeId===p.home_team_id&&f.awayId===p.away_team_id){
   patch={...gradePrediction(p,f.homeScore,f.awayScore),grade_status:"graded",graded_at:now.toISOString()};graded++;
  }else if(Date.parse(p.starts_at)<now.getTime()-7*DAY){
   patch={grade_status:"void",graded_at:now.toISOString()};voided++;   // postponed, cancelled or never reported
  }
  if(patch)await rest("rounders_predictions?id=eq."+p.id+"&grade_status=eq.pending",{method:"PATCH",headers:{Prefer:"return=minimal"},body:JSON.stringify(patch)});
 }
 return {graded,voided,pending:pending.length-graded-voided};
}

export type StoredPrediction=PredictionRecord&{
 id:number;market_spread_home:number|null;market_total:number|null;market_source:string|null;
 grade_status:"pending"|"graded"|"void";final_home:number|null;final_away:number|null;
 winner_correct:boolean|null;brier:number|null;margin_error:number|null;total_error:number|null;graded_at:string|null;
};
const COLUMNS="id,sport,provider,provider_event_id,season,starts_at,home,away,home_team_id,away_team_id,neutral,model_id,model_version,totals_model,predicted_at,"+
 "projected_home,projected_away,projected_margin,projected_total,home_win_probability,projected_winner,training_games,training_through,data_source,"+
 "market_spread_home,market_total,market_source,grade_status,final_home,final_away,winner_correct,brier,margin_error,total_error,graded_at";
/** Upcoming (not yet started) predictions plus games that started within the last 12 hours. */
export async function listUpcomingPredictions(sport:EngineSport,model:ModelId,now=new Date()):Promise<StoredPrediction[]>{
 const since=new Date(now.getTime()-12*HOUR).toISOString(),until=new Date(now.getTime()+8*DAY).toISOString();
 const r=await rest("rounders_predictions?select="+COLUMNS+"&sport=eq."+sport+"&model_id=eq."+encodeURIComponent(model)+
  "&starts_at=gte."+encodeURIComponent(since)+"&starts_at=lt."+encodeURIComponent(until)+"&order=starts_at.asc&limit=200");
 return await r.json() as StoredPrediction[];
}
export async function listGradedPredictions(sport:EngineSport,model:ModelId|null,limit=2000):Promise<StoredPrediction[]>{
 const r=await rest("rounders_predictions?select="+COLUMNS+"&sport=eq."+sport+(model?"&model_id=eq."+encodeURIComponent(model):"")+
  "&grade_status=eq.graded&order=starts_at.desc&limit="+Math.min(Math.max(limit,1),5000));
 return await r.json() as StoredPrediction[];
}
export function summarizeStored(rows:StoredPrediction[]):ForecastSummary{
 return summarizeForecasts(rows.filter(r=>r.final_home!==null&&r.final_away!==null).map(r=>({
  homeWinProbability:r.home_win_probability,projectedMargin:r.projected_margin,projectedTotal:r.projected_total,
  homeScore:r.final_home!,awayScore:r.final_away!,marketSpreadHome:r.market_spread_home,marketTotal:r.market_total
 })));
}

/** Daily: walk-forward backtest of every model on verified history, plus the promotion gate. */
export async function recordBacktest(sport:EngineSport,now=new Date()){
 const started=Date.now();
 const archive=await getVerifiedResearchGames(sport);
 const report=runBacktest(archive.games,sport,now,{maxWeeks:SPORT_CONFIG[sport].backtestWeeks});
 const champion=championFor(sport);
 const promotion=CANDIDATE_MODELS.filter(m=>m!==champion).map(m=>evaluatePromotion(report,champion,m));
 await rest("rounders_backtests?on_conflict=sport,engine_revision,run_day",{
  method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},
  body:JSON.stringify({sport,engine_revision:ENGINE_REVISION,run_day:now.toISOString().slice(0,10),data_source:archive.provider,champion,
   historical_games:report.historicalGames,evaluated_games:report.evaluatedGames,evaluated_weeks:report.evaluatedWeeks,
   seasons:report.seasons,from_game:report.from,through_game:report.through,
   models:report.models,totals:report.totals,promotion})
 });
 return {ms:Date.now()-started,evaluated:report.evaluatedGames,weeks:report.evaluatedWeeks,recommended:promotion.filter(p=>p.recommend).map(p=>p.challenger)};
}
export type StoredBacktest={sport:EngineSport;engine_revision:string;run_day:string;data_source:string;champion:string;
 historical_games:number;evaluated_games:number;evaluated_weeks:number;seasons:number[];from_game:string|null;through_game:string|null;
 models:Array<{model:ModelId;summary:ForecastSummary;sigma?:number}>;totals:unknown;promotion:unknown[]};
/** Latest backtest for the current engine revision; falls back to the newest earlier revision until one runs. */
export async function latestBacktest(sport:EngineSport):Promise<StoredBacktest|null>{
 const base="rounders_backtests?select=sport,engine_revision,run_day,data_source,champion,historical_games,evaluated_games,evaluated_weeks,seasons,from_game,through_game,models,totals,promotion&sport=eq."+sport;
 const current=await (await rest(base+"&engine_revision=eq."+encodeURIComponent(ENGINE_REVISION)+"&order=run_day.desc&limit=1")).json() as StoredBacktest[];
 if(current[0])return current[0];
 const any=await (await rest(base+"&order=run_day.desc,created_at.desc&limit=1")).json() as StoredBacktest[];
 return any[0]||null;
}

export async function findStoredPrediction(sport:EngineSport,eventId:string,model:ModelId):Promise<StoredPrediction|null>{
 if(!/^\d{1,20}$/.test(eventId))return null;
 const r=await rest("rounders_predictions?select="+COLUMNS+"&sport=eq."+sport+"&provider_event_id=eq."+eventId+"&model_id=eq."+encodeURIComponent(model)+"&order=predicted_at.asc&limit=1");
 const rows=await r.json() as StoredPrediction[];
 return rows[0]||null;
}

/** Every stored prediction of one model that involves a team, oldest first. */
export async function listTeamPredictions(sport:EngineSport,model:ModelId,team:string):Promise<StoredPrediction[]>{
 const q=`"${team.replace(/["\\]/g,"")}"`;
 const r=await rest("rounders_predictions?select="+COLUMNS+"&sport=eq."+sport+"&model_id=eq."+encodeURIComponent(model)+
  "&or="+encodeURIComponent(`(home.eq.${q},away.eq.${q})`)+"&grade_status=neq.void&order=starts_at.asc&limit=300");
 return await r.json() as StoredPrediction[];
}
