import {NextResponse} from "next/server";
import {planForRequest,subscriptionsFor} from "../../../lib/billing/server";
import {PLANS} from "../../../lib/billing/plans";

export const dynamic="force-dynamic";
export async function GET(req:Request){
 const {plan,user}=await planForRequest(req);
 if(!user)return NextResponse.json({signedIn:false,plan:"free"},{headers:{"Cache-Control":"no-store"}});
 const subs=await subscriptionsFor(user.id).catch(()=>[]);
 return NextResponse.json({signedIn:true,email:user.email,plan,planName:PLANS[plan].name,
  subscriptions:subs.map(s=>({plan:s.plan,status:s.status,currentPeriodEnd:s.current_period_end,cancelAtPeriodEnd:s.cancel_at_period_end})),
  testMode:true},{headers:{"Cache-Control":"no-store"}});
}
