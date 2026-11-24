import {hasFeature,type PlanId} from "./plans.ts";

/** Server-side field gating for a prediction. Free keeps winner + probability; nothing is hidden client-side only. */
export function gatePrediction<T extends {projectedHome:number|null;projectedAway:number|null;projectedSpreadHome:number|null;projectedTotal:number|null;market:unknown}>(p:T,plan:PlanId):T&{locked:string[]}{
 const locked:string[]=[];
 let out:T={...p};
 if(!hasFeature(plan,"predictions.lines")){out={...out,projectedHome:null,projectedAway:null,projectedSpreadHome:null,projectedTotal:null};locked.push("spread","total","score");}
 if(!hasFeature(plan,"predictions.market")){out={...out,market:null};locked.push("market");}
 return {...out,locked};
}
