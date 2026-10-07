import {NextResponse} from "next/server";
import {buildRatings,projectMatchup} from "../../../lib/ratings";
import {demoHistory} from "../../../lib/demoHistory";
import {getEspnResults} from "../../../lib/results/espn";
export const dynamic="force-dynamic";
export async function GET(req:Request){
 const {searchParams}=new URL(req.url),sport=(searchParams.get("sport")||"NBA").toUpperCase(),away=searchParams.get("away"),home=searchParams.get("home");
 if(!away||!home)return NextResponse.json({error:"away and home are required"},{status:400});
 let games=demoHistory(sport),trainingDataState:"external"|"simulated"="simulated",trainingProvider="controlled-demo",fallback=true,message="Controlled fallback history";
 try{const batch=await getEspnResults(sport);games=batch.games;trainingDataState=batch.source;trainingProvider=batch.provider;fallback=false;message=batch.message||""}catch(error){message=error instanceof Error?error.message:"External results unavailable"}
 const ratings=buildRatings(games);
 const baseline=sport==="NFL"?23:sport==="NHL"?3:sport==="MLB"?4.5:112;
 const hfa=sport==="NFL"?2.2:sport==="NHL"?.18:sport==="MLB"?.25:2.2;
 const projection=projectMatchup(ratings,away,home,baseline,hfa);
 if(!projection)return NextResponse.json({error:"No model coverage for matchup",state:"model",trainingDataState,trainingProvider,fallback,message},{status:404});
 return NextResponse.json({model:"rounders-v1",trainingDataState,trainingProvider,fallback,message,sampleGames:Math.floor(games.length/2),projection});
}
