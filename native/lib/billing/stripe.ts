import {createHmac,timingSafeEqual} from "node:crypto";
import {planForPrice} from "./plans.ts";

/**
 * Minimal Stripe REST client (no SDK). TEST MODE ONLY: any key that is not
 * sk_test_/rk_test_ is refused, so no live charge can be made from this code.
 */
export function stripeKey(env:Record<string,string|undefined>=process.env):string{
 const key=env.STRIPE_SECRET_KEY||"";
 if(!key)throw new Error("Billing is not configured");
 if(!/^(sk|rk)_test_[A-Za-z0-9]+$/.test(key))throw new Error("Refusing non-test Stripe key: live billing is not enabled");
 return key;
}
/** Stripe form encoding, including nested objects and arrays (a[b][0][c]=v). */
export function formEncode(data:Record<string,unknown>,prefix=""):string{
 const parts:string[]=[];
 for(const [k,v] of Object.entries(data)){
  if(v===undefined||v===null)continue;
  const name=prefix?`${prefix}[${k}]`:k;
  if(Array.isArray(v))v.forEach((item,i)=>{
   if(item!==null&&typeof item==="object")parts.push(formEncode(item as Record<string,unknown>,`${name}[${i}]`));
   else parts.push(encodeURIComponent(`${name}[${i}]`)+"="+encodeURIComponent(String(item)));
  });
  else if(typeof v==="object")parts.push(formEncode(v as Record<string,unknown>,name));
  else parts.push(encodeURIComponent(name)+"="+encodeURIComponent(String(v)));
 }
 return parts.filter(Boolean).join("&");
}
export async function stripe<T=Record<string,unknown>>(method:"GET"|"POST",path:string,data?:Record<string,unknown>,idempotencyKey?:string):Promise<T>{
 const key=stripeKey();
 const body=data&&method==="POST"?formEncode(data):undefined;
 const url="https://api.stripe.com/v1/"+path+(data&&method==="GET"?"?"+formEncode(data):"");
 const res=await fetch(url,{method,body,cache:"no-store",signal:AbortSignal.timeout(10000),
  headers:{Authorization:"Bearer "+key,"Content-Type":"application/x-www-form-urlencoded",...(idempotencyKey?{"Idempotency-Key":idempotencyKey}:{})}});
 const json=await res.json() as T&{error?:{message?:string;type?:string}};
 if(!res.ok)throw new Error("Stripe "+(json.error?.type||res.status)+": "+(json.error?.message||"request failed"));
 return json;
}

/** Verify a Stripe-Signature header (v1 HMAC-SHA256 over "<t>.<raw body>") with a timestamp tolerance. */
export function verifyStripeSignature(payload:string,header:string|null,secret:string,nowSeconds=Math.floor(Date.now()/1000),toleranceSeconds=300):boolean{
 if(!header||!secret)return false;
 const items=header.split(",").map(x=>x.trim().split("=",2));
 const t=Number(items.find(([k])=>k==="t")?.[1]);
 const signatures=items.filter(([k,v])=>k==="v1"&&typeof v==="string"&&/^[0-9a-f]{64}$/.test(v)).map(([,v])=>v);
 if(!Number.isInteger(t)||!signatures.length||Math.abs(nowSeconds-t)>toleranceSeconds)return false;
 const expected=Buffer.from(createHmac("sha256",secret).update(`${t}.${payload}`).digest("hex"),"hex");
 return signatures.some(s=>{const got=Buffer.from(s,"hex");return got.length===expected.length&&timingSafeEqual(got,expected);});
}

type StripeSubscription={
 id:string;customer:string|{id:string};status:string;cancel_at_period_end?:boolean;canceled_at?:number|null;livemode?:boolean;
 current_period_end?:number|null;metadata?:Record<string,string>;
 items?:{data?:Array<{price?:{id?:string};current_period_end?:number|null}>};
};
/** Stripe subscription -> rounders_subscriptions row. Newer API versions keep the period end on the item. */
export function subscriptionRow(sub:StripeSubscription,userId:string,env:Record<string,string|undefined>){
 const item=sub.items?.data?.[0];
 const priceId=item?.price?.id??null;
 const end=sub.current_period_end??item?.current_period_end??null;
 return {
  stripe_subscription_id:sub.id,user_id:userId,
  stripe_customer_id:typeof sub.customer==="string"?sub.customer:sub.customer.id,
  plan:planForPrice(priceId,env),price_id:priceId,status:sub.status,
  current_period_end:end?new Date(end*1000).toISOString():null,
  cancel_at_period_end:Boolean(sub.cancel_at_period_end),
  canceled_at:sub.canceled_at?new Date(sub.canceled_at*1000).toISOString():null,
  livemode:Boolean(sub.livemode),updated_at:new Date().toISOString()
 };
}
export type {StripeSubscription};
