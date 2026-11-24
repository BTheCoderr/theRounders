import {uniqueCompletedGames,type CompletedGame} from "../powerRatings.ts";
import type {TeamGame} from "../ratings";
import {ALL_MODELS,ENGINE_REVISION,fitMarginModel,type EngineSport,type MarginPredictor,type ModelId} from "./models.ts";
import {TOTALS_MODEL,fitTotals,leagueAverageTotal} from "./totals.ts";
import {buildSchedule} from "./v3.ts";
import {calibratedSigma} from "./calibration.ts";
import {SPORT_CONFIG,seasonFor} from "../sports.ts";
import {summarizeForecasts,winProbability,type ForecastSummary,type GradedForecast} from "./metrics.ts";

/**
 * Weekly walk-forward backtest.
 * At each Monday 00:00 UTC origin every model is refit on games that finished
 * before the origin, then predicts that week's games. Results of the week are
 * never visible to its own forecasts. All models are scored on the same games.
 * Win probabilities use σ calibrated from each model's own earlier out-of-sample
 * errors (weeks before the origin only), exactly as live predictions do.
 * These are simulated pregame forecasts on history, not live recorded predictions.
 */
export type ModelBacktest={model:ModelId;summary:ForecastSummary;sigma:number};
export type BacktestReport={
 method:"weekly-walk-forward";engineRevision:string;sport:EngineSport;
 asOf:string;from:string|null;through:string|null;
 historicalGames:number;evaluatedGames:number;evaluatedWeeks:number;skippedColdStart:number;
 seasons:number[];
 models:ModelBacktest[];
 totals:{model:string;summary:{games:number;mae:number|null;bias:number|null};baseline:{games:number;mae:number|null;bias:number|null}};
 /** Per-game absolute margin errors, aligned across models, for paired comparisons. */
 paired:Record<ModelId,number[]>;
 pairedBrier:Record<ModelId,number[]>;
};
const DAY=86400000;
export const weekStart=(t:number)=>{const d=new Date(t);return Date.UTC(d.getUTCFullYear(),d.getUTCMonth(),d.getUTCDate())-((d.getUTCDay()+6)%7)*DAY;};
/** Season label: the year the season began (MLB: the calendar year). */
export const seasonOf=(date:string,sport?:EngineSport)=>seasonFor(sport,date);

export function runBacktest(rows:TeamGame[],sport:EngineSport,asOf:Date,opts:{maxWeeks?:number;minTrainGames?:number;models?:readonly ModelId[]}={}):BacktestReport{
 const models=opts.models??ALL_MODELS;
 const maxWeeks=opts.maxWeeks??104,minTrain=opts.minTrainGames??SPORT_CONFIG[sport].minTrainGames;
 if(!(Number.isInteger(maxWeeks)&&maxWeeks>=1&&maxWeeks<=260))throw new Error("Invalid evaluation window");
 const history:CompletedGame[]=uniqueCompletedGames(rows,new Date(asOf.getTime()-1));
 // Schedule (dates only) for rest features: known before games are played, so not leakage.
 const schedule=buildSchedule(history);
 const groups=new Map<number,CompletedGame[]>();
 for(const g of history){const k=weekStart(Date.parse(g.date));groups.set(k,[...(groups.get(k)||[]),g]);}
 const weeks=[...groups.keys()].sort((a,b)=>a-b).slice(-maxWeeks);
 // Running out-of-sample squared margin errors per model, updated after each week.
 const sse=new Map<ModelId,number>(models.map(m=>[m,0])),sseN=new Map<ModelId,number>(models.map(m=>[m,0]));
 const forecasts=new Map<ModelId,GradedForecast[]>(models.map(m=>[m,[]]));
 const paired=Object.fromEntries(models.map(m=>[m,[] as number[]])) as Record<ModelId,number[]>;
 const pairedBrier=Object.fromEntries(models.map(m=>[m,[] as number[]])) as Record<ModelId,number[]>;
 let totN=0,totAbs=0,totBias=0,baseN=0,baseAbs=0,baseBias=0;
 let evaluated=0,evaluatedWeeks=0,skipped=0,from:string|null=null,through:string|null=null;
 const seasons=new Set<number>();
 for(const origin of weeks){
  const upcoming=groups.get(origin)||[];
  const originDate=new Date(origin);
  const train=history.filter(g=>Date.parse(g.date)<origin);
  if(train.length<minTrain){skipped+=upcoming.length;continue;}
  // Fit each base model once per week; the ensemble reuses these fits.
  const base=new Map<ModelId,MarginPredictor>();
  const fitOnce=(m:ModelId)=>{let f=base.get(m);if(!f){f=fitMarginModel(m,train,sport,originDate,schedule);base.set(m,f);}return f;};
  const predictors=new Map<ModelId,MarginPredictor>(models.map(m=>[m,m==="ensemble"
   ?((h:string,a:string,n:boolean,d?:string)=>{const parts=(["power-v2","rpi-v2.1","elo-margin","rounders-v3"] as ModelId[]).map(x=>fitOnce(x)(h,a,n,d));return parts.some(v=>v===null)?null:(parts as number[]).reduce((s,v)=>s+v,0)/parts.length;})
   :fitOnce(m)]));
  const totals=fitTotals(train,sport,originDate);
  const leagueTotal=leagueAverageTotal(train,sport,originDate);
  const sigmas=new Map<ModelId,number>(models.map(m=>[m,calibratedSigma(sport,sse.get(m)!,sseN.get(m)!)]));
  const weekErr:Array<[ModelId,number]>=[];
  let used=0;
  for(const g of upcoming){
   const margins=models.map(m=>predictors.get(m)!(g.home,g.away,g.neutral,g.date));
   const total=totals.predict(g.home,g.away,g.neutral);
   if(margins.some(x=>x===null||!Number.isFinite(x))||!total){skipped++;continue;}
   used++;evaluated++;seasons.add(seasonOf(g.date,sport));
   from??=g.date;through=g.date;
   const actualTotal=g.homeScore+g.awayScore,actualMargin=g.homeScore-g.awayScore;
   totN++;totAbs+=Math.abs(total.total-actualTotal);totBias+=total.total-actualTotal;
   if(leagueTotal!==null){baseN++;baseAbs+=Math.abs(leagueTotal-actualTotal);baseBias+=leagueTotal-actualTotal;}
   models.forEach((m,i)=>{
    const margin=margins[i]!,p=winProbability(margin,sigmas.get(m)!);
    weekErr.push([m,(margin-actualMargin)**2]);
    forecasts.get(m)!.push({homeWinProbability:p,projectedMargin:margin,projectedTotal:total.total,homeScore:g.homeScore,awayScore:g.awayScore});
    paired[m].push(Math.abs(margin-actualMargin));
    pairedBrier[m].push(actualMargin===0?NaN:(p-(actualMargin>0?1:0))**2);
   });
  }
  for(const [m,e] of weekErr){sse.set(m,sse.get(m)!+e);sseN.set(m,sseN.get(m)!+1);}
  if(used)evaluatedWeeks++;
 }
 const r=(x:number)=>Number(x.toFixed(4));
 return {
  method:"weekly-walk-forward",engineRevision:ENGINE_REVISION,sport,asOf:asOf.toISOString(),from,through,
  historicalGames:history.length,evaluatedGames:evaluated,evaluatedWeeks,skippedColdStart:skipped,
  seasons:[...seasons].sort((a,b)=>a-b),
  models:models.map(m=>({model:m,summary:summarizeForecasts(forecasts.get(m)!),sigma:r(calibratedSigma(sport,sse.get(m)!,sseN.get(m)!))})),
  totals:{model:TOTALS_MODEL,
   summary:{games:totN,mae:totN?r(totAbs/totN):null,bias:totN?r(totBias/totN):null},
   baseline:{games:baseN,mae:baseN?r(baseAbs/baseN):null,bias:baseN?r(baseBias/baseN):null}},
  paired,pairedBrier
 };
}
