/** Margin-to-probability mapping and scoring metrics shared by backtests and live grading. */

/** Standard normal CDF (Abramowitz-Stegun 7.1.26, |error| < 1.5e-7). */
export function normalCdf(x:number):number{
 const t=1/(1+0.3275911*Math.abs(x)/Math.SQRT2);
 const y=1-((((1.061405429*t-1.453152027)*t+1.421413741)*t-0.284496736)*t+0.254829592)*t*Math.exp(-(x*x)/2);
 return x>=0?(1+y)/2:(1-y)/2;
}
/** Home win probability (0..1) for a projected home margin. Clipped away from 0 and 1. */
export function winProbability(margin:number,sigma:number):number{
 if(!Number.isFinite(margin)||!(sigma>0))throw new Error("Invalid margin or sigma");
 return Math.min(0.995,Math.max(0.005,normalCdf(margin/sigma)));
}

/** One forecast paired with its final result. */
export type GradedForecast={
 homeWinProbability:number;          // 0..1
 projectedMargin:number;             // home minus away
 projectedTotal:number|null;
 homeScore:number;awayScore:number;
 marketSpreadHome?:number|null;      // home line, e.g. -3.5, when a real pregame line was captured
 marketTotal?:number|null;
};
export type CalibrationBucket={from:number;to:number;forecasts:number;meanForecast:number|null;observedRate:number|null};
export type ForecastSummary={
 games:number;decided:number;
 winnerAccuracy:number|null;        // share of decided games (ties excluded)
 brierScore:number|null;            // decided games, lower is better
 logLoss:number|null;
 marginMAE:number|null;marginRMSE:number|null;marginBias:number|null;
 totalGames:number;totalMAE:number|null;totalBias:number|null;
 calibration:CalibrationBucket[];
 againstSpread:{games:number;wins:number;losses:number;pushes:number;winRate:number|null};
 againstTotal:{games:number;wins:number;losses:number;pushes:number;winRate:number|null};
};
const r4=(n:number)=>Number(n.toFixed(4));
/**
 * Calibration uses the probability of the side the model favored (0.5..1),
 * in five 10-point buckets, so the reader sees whether "70%" picks win about 70%.
 */
export function summarizeForecasts(rows:GradedForecast[]):ForecastSummary{
 let decided=0,correct=0,brier=0,logloss=0,absM=0,sqM=0,biasM=0,totN=0,absT=0,biasT=0;
 const edges=[0.5,0.6,0.7,0.8,0.9,1.0001];
 const buckets=edges.slice(0,-1).map((from,i)=>({from,to:Math.min(1,edges[i+1]),n:0,sumP:0,hits:0}));
 const ats={games:0,wins:0,losses:0,pushes:0},ou={games:0,wins:0,losses:0,pushes:0};
 for(const r of rows){
  const margin=r.homeScore-r.awayScore;
  const err=r.projectedMargin-margin;
  absM+=Math.abs(err);sqM+=err*err;biasM+=err;
  if(r.projectedTotal!==null&&Number.isFinite(r.projectedTotal)){
   const te=r.projectedTotal-(r.homeScore+r.awayScore);
   totN++;absT+=Math.abs(te);biasT+=te;
  }
  if(margin!==0){
   decided++;
   const y=margin>0?1:0,p=r.homeWinProbability;
   if((p>=0.5?1:0)===y)correct++;
   brier+=(p-y)**2;
   const pc=Math.min(1-1e-6,Math.max(1e-6,p));
   logloss+=-(y*Math.log(pc)+(1-y)*Math.log(1-pc));
   const favP=Math.max(p,1-p),favWon=(p>=0.5)===(y===1);
   const b=buckets.find(x=>favP>=x.from&&favP<x.to)??buckets[buckets.length-1];
   b.n++;b.sumP+=favP;if(favWon)b.hits++;
  }
  // Against the spread: does the model side (projection vs market line) cover?
  if(r.marketSpreadHome!==undefined&&r.marketSpreadHome!==null&&Number.isFinite(r.marketSpreadHome)){
   const edge=r.projectedMargin+r.marketSpreadHome;   // >0: model likes home to cover
   if(edge!==0){
    const cover=margin+r.marketSpreadHome;
    ats.games++;
    if(cover===0)ats.pushes++;
    else if((cover>0)===(edge>0))ats.wins++;else ats.losses++;
   }
  }
  if(r.marketTotal!==undefined&&r.marketTotal!==null&&r.projectedTotal!==null&&Number.isFinite(r.marketTotal)){
   const lean=r.projectedTotal-r.marketTotal,actual=r.homeScore+r.awayScore-r.marketTotal;
   if(lean!==0){
    ou.games++;
    if(actual===0)ou.pushes++;
    else if((actual>0)===(lean>0))ou.wins++;else ou.losses++;
   }
  }
 }
 const n=rows.length;
 const atsDecided=ats.wins+ats.losses,ouDecided=ou.wins+ou.losses;
 return {
  games:n,decided,
  winnerAccuracy:decided?r4(correct/decided):null,
  brierScore:decided?r4(brier/decided):null,
  logLoss:decided?r4(logloss/decided):null,
  marginMAE:n?r4(absM/n):null,marginRMSE:n?r4(Math.sqrt(sqM/n)):null,marginBias:n?r4(biasM/n):null,
  totalGames:totN,totalMAE:totN?r4(absT/totN):null,totalBias:totN?r4(biasT/totN):null,
  calibration:buckets.map(b=>({from:b.from,to:b.to,forecasts:b.n,meanForecast:b.n?r4(b.sumP/b.n):null,observedRate:b.n?r4(b.hits/b.n):null})),
  againstSpread:{...ats,winRate:atsDecided?r4(ats.wins/atsDecided):null},
  againstTotal:{...ou,winRate:ouDecided?r4(ou.wins/ouDecided):null}
 };
}
