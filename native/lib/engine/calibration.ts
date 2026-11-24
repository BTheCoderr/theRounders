import {SPORT_SETTINGS,type EngineSport} from "./models.ts";

/**
 * Win-probability calibration.
 * p(home wins) = Φ(margin / σ). Under normally distributed forecast errors the
 * maximum-likelihood σ is the root-mean-square of out-of-sample margin errors,
 * so σ is learned from each model's own past misses instead of being assumed.
 * Until enough out-of-sample games exist, the documented sport default is used.
 * The result is clamped to a sane band around that default.
 */
export const MIN_CALIBRATION_GAMES:Record<EngineSport,number>={NBA:300,NFL:150};
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
