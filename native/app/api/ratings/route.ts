import {NextResponse} from "next/server";
import {buildRatings,projectMatchup} from "../../../lib/ratings";
import {demoHistory} from "../../../lib/demoHistory";
export const dynamic="force-dynamic";
export async function GET(req:Request){
 const {searchParams}=new URL(req.url),sport=(searchParams.get("sport")||"NBA").toUpperCase(),away=searchParams.get("away"),home=searchParams.get("home");
 if(!away||!home)return NextResponse.json({error:"away and home are required"},{status:400});
 const ratings=buildRatings(demoHistory(sport));
 const baseline=sport==="NFL"?23:sport==="NHL"?3:sport==="MLB"?4.5:112;
 const hfa=sport==="NFL"?2.2:sport==="NHL"?.18:sport==="MLB"?.25:2.2;
 const projection=projectMatchup(ratings,away,home,baseline,hfa);
 if(!projection)return NextResponse.json({error:"No model coverage for matchup",state:"model"},{status:404});
 return NextResponse.json({model:"rounders-v1",trainingDataState:"simulated",projection});
}
