import {rest,archiveConfigured} from "../persistence/history";
import {entitledPlan,type PlanId,type SubscriptionState} from "./plans";

export type SessionUser={id:string;email:string|null};
/** Verify the Supabase access token sent as "Authorization: Bearer <token>". */
export async function userFromRequest(req:Request):Promise<SessionUser|null>{
 const header=req.headers.get("authorization")||"";
 const token=/^Bearer\s+([A-Za-z0-9._-]{20,4096})$/.exec(header)?.[1];
 const url=process.env.SUPABASE_URL||process.env.NEXT_PUBLIC_SUPABASE_URL,key=process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
 if(!token||!url||!key)return null;
 try{
  const r=await fetch(url+"/auth/v1/user",{headers:{apikey:key,Authorization:"Bearer "+token},cache:"no-store",signal:AbortSignal.timeout(5000)});
  if(!r.ok)return null;
  const u=await r.json() as {id?:string;email?:string};
  return u.id&&/^[0-9a-f-]{36}$/i.test(u.id)?{id:u.id,email:u.email??null}:null;
 }catch{return null}
}
export async function subscriptionsFor(userId:string):Promise<Array<SubscriptionState&{stripe_subscription_id:string;price_id:string|null}>>{
 const r=await rest("rounders_subscriptions?select=stripe_subscription_id,plan,status,price_id,current_period_end,cancel_at_period_end&user_id=eq."+encodeURIComponent(userId));
 return await r.json();
}
/** Plan for this request. Any failure (no token, storage down) resolves to Free, never to a paid plan. */
export async function planForRequest(req:Request):Promise<{plan:PlanId;user:SessionUser|null}>{
 const user=await userFromRequest(req);
 if(!user||!archiveConfigured())return {plan:"free",user};
 try{return {plan:entitledPlan(await subscriptionsFor(user.id)),user}}
 catch{return {plan:"free",user}}
}
export async function customerFor(userId:string):Promise<string|null>{
 const r=await rest("rounders_customers?select=stripe_customer_id&user_id=eq."+encodeURIComponent(userId)+"&limit=1");
 const rows=await r.json() as Array<{stripe_customer_id:string}>;
 return rows[0]?.stripe_customer_id??null;
}
export async function userForCustomer(customerId:string):Promise<string|null>{
 const r=await rest("rounders_customers?select=user_id&stripe_customer_id=eq."+encodeURIComponent(customerId)+"&limit=1");
 const rows=await r.json() as Array<{user_id:string}>;
 return rows[0]?.user_id??null;
}
export async function saveCustomer(userId:string,customerId:string,email:string|null){
 await rest("rounders_customers?on_conflict=user_id",{method:"POST",headers:{Prefer:"resolution=ignore-duplicates,return=minimal"},
  body:JSON.stringify({user_id:userId,stripe_customer_id:customerId,email})});
}
export async function saveSubscription(row:Record<string,unknown>){
 await rest("rounders_subscriptions?on_conflict=stripe_subscription_id",{method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},body:JSON.stringify(row)});
}
/** Returns false when the event was already processed. */
export async function recordStripeEvent(id:string,type:string):Promise<boolean>{
 const r=await rest("rounders_stripe_events?on_conflict=id",{method:"POST",headers:{Prefer:"resolution=ignore-duplicates,return=representation"},body:JSON.stringify({id,type,livemode:false})});
 const rows=await r.json() as unknown[];
 return Array.isArray(rows)&&rows.length>0;
}
export function siteOrigin(req:Request):string{
 const configured=process.env.ROUNDERS_SITE_URL;
 if(configured&&/^https:\/\/[a-z0-9.-]+$/i.test(configured))return configured;
 return new URL(req.url).origin;
}
