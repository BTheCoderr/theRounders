/**
 * Spending controls for paid data providers.
 * Every paid call asks `decideSpend` first. Nothing is fetched unless the provider is
 * explicitly enabled and has a key; monthly and daily credit caps leave headroom below
 * the purchased plan, and the provider's own "remaining" header is respected.
 */
export type Provider="the-odds-api"|"balldontlie";
export type SpendPolicy={enabled:boolean;monthlyCredits:number;budgetFraction:number;dailyFraction:number};
export type SpendState={monthUsed:number;dayUsed:number;lastRemaining:number|null};
export type SpendDecision={allow:boolean;reason:string};

const num=(v:string|undefined,d:number)=>{const n=Number(v);return Number.isFinite(n)&&n>=0?n:d;};
/** Policy from environment. Off unless <PROVIDER>_ENABLED=1 and an API key is set. */
export function spendPolicy(provider:Provider,env:Record<string,string|undefined>=process.env):SpendPolicy{
 if(provider==="the-odds-api")return {
  enabled:env.ODDS_INGEST_ENABLED==="1"&&Boolean(env.ODDS_API_KEY),
  monthlyCredits:num(env.ODDS_MONTHLY_CREDITS,0),        // the purchased plan, e.g. 20000
  budgetFraction:Math.min(1,num(env.ODDS_BUDGET_FRACTION,0.85)),
  dailyFraction:Math.min(1,num(env.ODDS_DAILY_FRACTION,0.06))};
 // BALLDONTLIE plans are flat-price with rate limits, not credits: count requests against a monthly ceiling.
 return {
  enabled:env.BALLDONTLIE_ENABLED==="1"&&Boolean(env.BALLDONTLIE_API_KEY),
  monthlyCredits:num(env.BALLDONTLIE_MONTHLY_REQUESTS,60000),
  budgetFraction:1,dailyFraction:Math.min(1,num(env.BALLDONTLIE_DAILY_FRACTION,0.1))};
}
/** Pure decision: may a call costing `cost` credits go ahead? */
export function decideSpend(policy:SpendPolicy,state:SpendState,cost:number):SpendDecision{
 if(!policy.enabled)return {allow:false,reason:"provider disabled"};
 if(!(policy.monthlyCredits>0))return {allow:false,reason:"no monthly credit plan configured"};
 if(!(cost>0))return {allow:false,reason:"invalid cost"};
 const monthCap=Math.floor(policy.monthlyCredits*policy.budgetFraction);
 const dayCap=Math.max(cost,Math.floor(policy.monthlyCredits*policy.dailyFraction));
 if(state.monthUsed+cost>monthCap)return {allow:false,reason:`monthly budget reached (${state.monthUsed}/${monthCap})`};
 if(state.dayUsed+cost>dayCap)return {allow:false,reason:`daily budget reached (${state.dayUsed}/${dayCap})`};
 // Keep a reserve on the provider's own counter (it may include usage from other apps on the key).
 const reserve=Math.ceil(policy.monthlyCredits*(1-policy.budgetFraction));
 if(state.lastRemaining!==null&&state.lastRemaining-cost<reserve)return {allow:false,reason:`provider quota reserve (${state.lastRemaining} left)`};
 return {allow:true,reason:"ok"};
}
/** The Odds API odds endpoint: cost = markets x regions (docs v4). */
export const oddsCost=(markets:number,regions:number)=>Math.max(1,markets)*Math.max(1,regions);
