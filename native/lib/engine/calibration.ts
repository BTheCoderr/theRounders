import {SPORT_SETTINGS,type EngineSport} from "./models.ts";
import {SPORT_CONFIG} from "../sports.ts";

/**
 * Win-probability calibration.
 * p(home wins) = Φ(margin / σ). Under normally distributed forecast errors the
 * maximum-likelihood σ is the root-mean-square of out-of-sample margin errors,
 * so σ is learned from each model's own past misses instead of being assumed.
 * Until enough out-of-sample games exist, the documented sport default is used.
 * The result is clamped to a sane band around that default.
 */
export const MIN_CALIBRATION_GAMES=Object.fromEntries(Object.entries(SPORT_CONFIG).map(([s,c])=>[s,c.calibrationGames])) as Record<EngineSport,number>;
export function calibratedSigma(sport:EngineSport,sumSquaredError:number,games:number):number{
 const fallback=SPORT_SETTINGS[sport].marginSigma;
 if(!(games>=MIN_CALIBRATION_GAMES[sport])||!(sumSquaredError>0))return fallback;
 const rmse=Math.sqrt(sumSquaredError/games);
 return Math.min(fallback*1.5,Math.max(fallback*0.75,rmse));
}
/** σ for live predictions from a stored backtest summary (its out-of-sample RMSE and game count). */
export function sigmaFromSummary(sport:EngineSport,summary:{games?:number;marginRMSE?:number|null}|null|undefined):number{
 const n=summary?.games??0,rmse=summary?.marginRMSE;
 return typeof rmse==="number"&&Number.isFinite(rmse)?calibratedSigma(sport,rmse*rmse*n,n):SPORT_SETTINGS[sport].marginSigma;
}

/**
 * Platt scaling, a sport-specific alternative to the normal mapping:
 *   p(home wins) = 1 / (1 + exp(-(a * margin + b)))
 * Fitted by Newton's method on out-of-sample (margin, outcome) pairs with a small ridge
 * penalty. b absorbs any systematic home/away bias the margin model leaves behind.
 * Ties are excluded. Returns null when there is too little data to fit.
 */
export type Platt={a:number;b:number;games:number};
export function fitPlatt(pairs:ReadonlyArray<{margin:number;won:0|1}>,minGames=200,ridge=1):Platt|null{
 const xs=pairs.filter(p=>Number.isFinite(p.margin));
 if(xs.length<minGames)return null;
 let a=0.1,b=0;
 for(let it=0;it<50;it++){
  let ga=-ridge*a,gb=-ridge*b,haa=-ridge,hab=0,hbb=-ridge;
  for(const {margin:x,won:y} of xs){
   const p=1/(1+Math.exp(-(a*x+b))),w=p*(1-p);
   ga+=(y-p)*x;gb+=(y-p);haa-=w*x*x;hab-=w*x;hbb-=w;
  }
  const det=haa*hbb-hab*hab;if(!(Math.abs(det)>1e-12))break;
  const da=(hbb*ga-hab*gb)/det,db=(haa*gb-hab*ga)/det;
  a-=da;b-=db;
  if(Math.abs(da)<1e-9&&Math.abs(db)<1e-9)break;
 }
 return Number.isFinite(a)&&Number.isFinite(b)&&a>0?{a,b,games:xs.length}:null;
}
export const plattProbability=(p:Platt,margin:number)=>Math.min(0.995,Math.max(0.005,1/(1+Math.exp(-(p.a*margin+p.b)))));
