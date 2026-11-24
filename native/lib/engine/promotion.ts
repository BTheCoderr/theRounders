import type {BacktestReport} from "./backtest";
import {CANDIDATE_MODELS,type EngineSport,type ModelId} from "./models.ts";

/**
 * A challenger replaces the champion only when, on the SAME out-of-sample games:
 *  1. there are enough games across at least two seasons,
 *  2. its margin error is lower by more than two standard errors of the paired difference,
 *  3. its Brier score is not worse.
 * Passing the gate produces a recommendation; switching the live champion is a
 * deliberate configuration change (ROUNDERS_CHAMPION_<SPORT>), never automatic.
 */
export const MIN_GATE_GAMES:Record<EngineSport,number>={NBA:600,NFL:250};
export type PromotionDecision={
 champion:ModelId;challenger:ModelId;recommend:boolean;
 games:number;seasons:number;
 maeDifference:number|null;standardError:number|null;brierDifference:number|null;
 reasons:string[];
};
function paired(a:number[],b:number[]){
 const d:number[]=[];
 for(let i=0;i<Math.min(a.length,b.length);i++){const x=a[i]-b[i];if(Number.isFinite(x))d.push(x);}
 if(d.length<2)return {n:d.length,mean:null as number|null,se:null as number|null};
 const mean=d.reduce((s,x)=>s+x,0)/d.length;
 const variance=d.reduce((s,x)=>s+(x-mean)**2,0)/(d.length-1);
 return {n:d.length,mean,se:Math.sqrt(variance/d.length)};
}
export function evaluatePromotion(report:BacktestReport,champion:ModelId,challenger:ModelId):PromotionDecision{
 const reasons:string[]=[];
 const r=(x:number|null)=>x===null?null:Number(x.toFixed(4));
 const mae=paired(report.paired[challenger]||[],report.paired[champion]||[]);   // negative = challenger better
 const brier=paired(report.pairedBrier[challenger]||[],report.pairedBrier[champion]||[]);
 const min=MIN_GATE_GAMES[report.sport];
 if(challenger===champion)reasons.push("Challenger is already the champion.");
 if(!(CANDIDATE_MODELS as readonly string[]).includes(challenger))reasons.push("Benchmarks cannot be promoted.");
 if(mae.n<min)reasons.push(`Only ${mae.n} paired games; the gate needs ${min}.`);
 if(report.seasons.length<2)reasons.push("Out-of-sample games cover fewer than two seasons.");
 if(mae.mean===null||mae.se===null)reasons.push("Margin errors unavailable.");
 else if(!(mae.mean< -2*mae.se))reasons.push("Margin error is not lower by more than two standard errors.");
 if(brier.mean===null)reasons.push("Brier scores unavailable.");
 else if(brier.mean>0)reasons.push("Brier score is worse than the champion's.");
 return {champion,challenger,recommend:reasons.length===0,games:mae.n,seasons:report.seasons.length,
  maeDifference:r(mae.mean),standardError:r(mae.se),brierDifference:r(brier.mean),
  reasons:reasons.length?reasons:["Passes the out-of-sample gate. Review, then set the champion explicitly."]};
}
/**
 * Live model per sport when ROUNDERS_CHAMPION_<SPORT> is unset. Changed only after the
 * promotion gate recommended it on real out-of-sample games:
 *  NBA 2026-11-24: power-v2 beat rounders-v1 over 4,890 games (Brier 0.2145 vs 0.2439).
 */
export const DEFAULT_CHAMPION:Record<EngineSport,ModelId>={NBA:"power-v2",NFL:"rounders-v1"};
export function championFor(sport:EngineSport,env:Record<string,string|undefined>=typeof process!=="undefined"?process.env:{}):ModelId{
 const configured=env["ROUNDERS_CHAMPION_"+sport];
 return configured&&(CANDIDATE_MODELS as readonly string[]).includes(configured)?configured as ModelId:DEFAULT_CHAMPION[sport];
}
