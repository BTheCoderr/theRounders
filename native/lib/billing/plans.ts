/** Plans, prices and features. Prices are proposals and are charged only in Stripe TEST mode. */
export type PlanId="free"|"pro"|"edge";
export type Feature=
 |"predictions.winner"        // projected winner + win probability (free)
 |"predictions.lines"         // projected spread, total and score
 |"predictions.market"        // stored live market line + model-vs-market difference
 |"predictions.challengers"   // every candidate model's prediction for each game
 |"ai.generative"             // LLM matchup commentary (when enabled server-side)
 |"export.history";           // CSV of graded prediction history
export const PLANS:Record<PlanId,{name:string;monthlyUsd:number;priceEnv?:string;features:Feature[];pitch:string[]}>={
 free:{name:"Free",monthlyUsd:0,features:["predictions.winner"],
  pitch:["Daily NBA and weekly NFL projected winners with win probabilities","Power Index rankings","The full public track record: accuracy, Brier score and calibration","Model explanations for every game","Line shop and paper bankroll"]},
 pro:{name:"Rounders Pro",monthlyUsd:19.99,priceEnv:"STRIPE_PRICE_PRO",features:["predictions.winner","predictions.lines","ai.generative","export.history"],
  pitch:["Everything in Free","Projected spreads, totals and final scores for every NBA and NFL game","Generative matchup analysis grounded in the stored prediction (when enabled)","CSV export of every graded prediction"]},
 edge:{name:"Rounders Edge",monthlyUsd:39.99,priceEnv:"STRIPE_PRICE_EDGE",features:["predictions.winner","predictions.lines","predictions.market","predictions.challengers","ai.generative","export.history"],
  pitch:["Everything in Pro","Model versus live market line on every prediction where a line was captured","Side-by-side predictions from every candidate model, including challengers not yet promoted","Exports include every model"]}
};
export const hasFeature=(plan:PlanId,f:Feature)=>PLANS[plan].features.includes(f);
export const isPaidPlan=(p:string):p is "pro"|"edge"=>p==="pro"||p==="edge";
/** Map a Stripe price ID to a plan using the configured price env vars. */
export function planForPrice(priceId:string|null|undefined,env:Record<string,string|undefined>):"pro"|"edge"|null{
 if(!priceId)return null;
 if(env.STRIPE_PRICE_EDGE&&priceId===env.STRIPE_PRICE_EDGE)return "edge";
 if(env.STRIPE_PRICE_PRO&&priceId===env.STRIPE_PRICE_PRO)return "pro";
 return null;
}
export type SubscriptionState={plan:"pro"|"edge"|null;status:string;current_period_end:string|null;cancel_at_period_end:boolean};
/**
 * Entitled plan from stored subscriptions.
 *  active / trialing         -> plan (a scheduled cancellation keeps access to period end)
 *  past_due                  -> plan until the paid period ends
 *  canceled / unpaid / incomplete / paused -> free
 * The best plan wins when several subscriptions exist.
 */
export function entitledPlan(subs:SubscriptionState[],now=new Date()):PlanId{
 let best:PlanId="free";
 for(const s of subs){
  if(!s.plan)continue;
  const periodOpen=s.current_period_end?Date.parse(s.current_period_end)>now.getTime():false;
  const ok=s.status==="active"||s.status==="trialing"?(periodOpen||!s.current_period_end):s.status==="past_due"&&periodOpen;
  if(ok&&(best==="free"||(best==="pro"&&s.plan==="edge")))best=s.plan;
 }
 return best;
}
