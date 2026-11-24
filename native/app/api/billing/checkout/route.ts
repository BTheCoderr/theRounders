import {NextResponse} from "next/server";
import {PLANS,isPaidPlan,entitledPlan} from "../../../../lib/billing/plans";
import {stripe} from "../../../../lib/billing/stripe";
import {customerFor,saveCustomer,siteOrigin,subscriptionsFor,userFromRequest} from "../../../../lib/billing/server";

export const dynamic="force-dynamic";
const json=(d:unknown,status=200)=>NextResponse.json(d,{status,headers:{"Cache-Control":"no-store"}});
/** Start a Stripe Checkout (test mode) subscription for the signed-in user. */
export async function POST(req:Request){
 const user=await userFromRequest(req);
 if(!user)return json({error:"Sign in with your email link first."},401);
 let plan:unknown;
 try{plan=(await req.json() as {plan?:unknown}).plan}catch{return json({error:"Expected JSON"},400)}
 if(typeof plan!=="string"||!isPaidPlan(plan))return json({error:"Choose pro or edge"},400);
 const price=process.env[PLANS[plan].priceEnv!];
 if(!price||!/^price_[A-Za-z0-9]+$/.test(price))return json({error:"Billing is not configured yet."},503);
 try{
  const subs=await subscriptionsFor(user.id);
  // One subscription per account: plan changes and cancellations go through the billing portal.
  if(entitledPlan(subs)!=="free"||subs.some(s=>["active","trialing","past_due","incomplete"].includes(s.status)))
   return json({error:"You already have a subscription. Use Manage billing to change or cancel it.",manage:true},409);
  let customer=await customerFor(user.id);
  if(!customer){
   const c=await stripe<{id:string}>("POST","customers",{email:user.email??undefined,metadata:{user_id:user.id}},"rounders-customer-"+user.id);
   customer=c.id;await saveCustomer(user.id,customer,user.email);
  }
  const origin=siteOrigin(req);
  const session=await stripe<{url:string}>("POST","checkout/sessions",{
   mode:"subscription",customer,client_reference_id:user.id,
   line_items:[{price,quantity:1}],
   // Flexible billing mode: accurate prorations on Pro <-> Edge changes in the portal.
   subscription_data:{billing_mode:{type:"flexible"},metadata:{user_id:user.id,plan}},
   allow_promotion_codes:true,
   metadata:{user_id:user.id,plan},
   success_url:origin+"/account?checkout=success&session_id={CHECKOUT_SESSION_ID}",cancel_url:origin+"/pricing?checkout=cancelled"
  });
  return json({url:session.url});
 }catch(e){
  const msg=e instanceof Error?e.message:"";
  return json({error:/non-test/.test(msg)?"Live billing is disabled.":"Checkout could not be started."},/non-test|not configured/.test(msg)?503:502);
 }
}
