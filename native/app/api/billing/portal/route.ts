import {NextResponse} from "next/server";
import {stripe} from "../../../../lib/billing/stripe";
import {customerFor,siteOrigin,userFromRequest} from "../../../../lib/billing/server";

export const dynamic="force-dynamic";
/** Stripe customer portal: change plan (Pro/Edge), update card, cancel (at period end). */
export async function POST(req:Request){
 const user=await userFromRequest(req);
 if(!user)return NextResponse.json({error:"Sign in first."},{status:401});
 try{
  const customer=await customerFor(user.id);
  if(!customer)return NextResponse.json({error:"No billing account yet."},{status:404});
  const s=await stripe<{url:string}>("POST","billing_portal/sessions",{customer,return_url:siteOrigin(req)+"/account"});
  return NextResponse.json({url:s.url},{headers:{"Cache-Control":"no-store"}});
 }catch{return NextResponse.json({error:"Billing portal unavailable."},{status:502})}
}
