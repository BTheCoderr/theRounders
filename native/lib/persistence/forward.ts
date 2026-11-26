import {rest} from "./history";
import {summarizeForecasts} from "../engine/metrics";
import type {Sport} from "../sports";

/**
 * Forward test of injury-v4: for each graded game, the LAST adjusted forecast made before
 * start vs the locked power-v2 pick on the SAME game. Nothing here exists in backtests,
 * because injury reports are only available going forward.
 */
export async function forwardInjuryReport(sport:"NBA"|"NFL"){
 const r=await rest(`rounders_adjusted_forecasts?select=provider_event_id,base_prediction_id,forecast_at,projected_margin,home_win_probability,final_home,final_away&sport=eq.${sport}&graded_at=not.is.null&order=forecast_at.desc&limit=5000`);
 const rows=await r.json() as Array<{provider_event_id:string;base_prediction_id:number;forecast_at:string;projected_margin:number;home_win_probability:number;final_home:number;final_away:number}>;
 const last=new Map<string,typeof rows[number]>();
 for(const x of rows)if(!last.has(x.provider_event_id))last.set(x.provider_event_id,x);
 const adj=[...last.values()];
 const ids=[...new Set(adj.map(a=>a.base_prediction_id))];
 const base=new Map<number,{projected_margin:number;home_win_probability:number}>();
 for(let i=0;i<ids.length;i+=100)
  for(const b of await (await rest(`rounders_predictions?select=id,projected_margin,home_win_probability&id=in.(${ids.slice(i,i+100).join(",")})`)).json() as Array<{id:number;projected_margin:number;home_win_probability:number}>)base.set(b.id,b);
 const paired=adj.filter(a=>base.has(a.base_prediction_id));
 const sum=(pick:(a:typeof paired[number])=>{projected_margin:number;home_win_probability:number})=>summarizeForecasts(paired.map(a=>{const p=pick(a);
  return {homeWinProbability:p.home_win_probability,projectedMargin:p.projected_margin,projectedTotal:null,homeScore:a.final_home,awayScore:a.final_away,marketSpreadHome:null,marketTotal:null};}));
 return {games:paired.length,injuryV4:sum(a=>a),powerV2SameGames:sum(a=>base.get(a.base_prediction_id)!)};
}
export const isInjurySport=(s:Sport):s is "NBA"|"NFL"=>s==="NBA"||s==="NFL";
