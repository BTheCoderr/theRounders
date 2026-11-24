import {NextResponse} from "next/server";
import {stripe,subscriptionRow,verifyStripeSignature,type StripeSubscription} from "../../../../lib/billing/stripe";
import {recordStripeEvent,saveSubscription,userForCustomer} from "../../../../lib/billing/server";
import {subscriptionIdFromEvent} from "../../../../lib/billing/events";

export const dynamic="force-dynamic";
const HANDLED=new Set(["checkout.session.completed","customer.subscription.created","customer.subscription.updated","customer.subscription.deleted","invoice.paid","invoice.payment_failed"]);
/**
 * Stripe webhook (test mode). Every handled event re-reads the subscription from Stripe,
 * so out-of-order or repeated deliveries converge on Stripe's current state.
 */
export async function POST(req:Request){
 const secret=process.env.STRIPE_WEBHOOK_SECRET||"";
 const payload=await req.text();
 if(!verifyStripeSignature(payload,req.headers.get("stripe-signature"),secret))return NextResponse.json({error:"Invalid signature"},{status:400});
 let event:{id:string;type:string;livemode:boolean;data:{object:Record<string,unknown>}};
 try{event=JSON.parse(payload)}catch{return NextResponse.json({error:"Invalid payload"},{status:400})}
 if(event.livemode)return NextResponse.json({error:"Live-mode events are not accepted"},{status:400});
 if(!HANDLED.has(event.type))return NextResponse.json({received:true,ignored:event.type});
 const o=event.data.object;
 const subscriptionId=subscriptionIdFromEvent(event.type,o);
 if(!subscriptionId||!/^sub_[A-Za-z0-9]+$/.test(subscriptionId))return NextResponse.json({received:true,skipped:"no subscription"});
 try{
  const sub=await stripe<StripeSubscription>("GET","subscriptions/"+subscriptionId,{"expand[]":"items.data.price"});
  if(sub.livemode)return NextResponse.json({error:"Live-mode subscription"},{status:400});
  const customer=typeof sub.customer==="string"?sub.customer:sub.customer.id;
  const userId=sub.metadata?.user_id||await userForCustomer(customer);
  if(!userId||!/^[0-9a-f-]{36}$/i.test(userId))return NextResponse.json({error:"Unknown customer"},{status:500});
  await saveSubscription(subscriptionRow(sub,userId,process.env));
  await recordStripeEvent(event.id,event.type);
  return NextResponse.json({received:true});
 }catch{
  // 500 makes Stripe retry later.
  return NextResponse.json({error:"Processing failed"},{status:500});
 }
}
