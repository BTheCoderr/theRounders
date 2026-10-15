import {NextResponse} from "next/server";
import {buildRatings,projectMatchup} from "../../../lib/ratings";
import {getTrainingGames} from "../../../lib/persistence/history";
export const dynamic="force-dynamic";
export async function GET(req:Request){
 const {searchParams}=new URL(req.url),sport=(searchParams.get("sport")||"NBA").toUpperCase(),away=searchParams.get("away"),home=searchParams.get("home");
 if(!["NBA","NFL","NHL","MLB"].includes(sport)||!away||!home||away.length>80||home.length>80||away===home)return NextResponse.json({error:"Valid sport, away and home are required"},{status:400});
 const batch=await getTrainingGames(sport as "NBA"|"NFL"|"NHL"|"MLB");
 const games=batch.games,trainingDataState=batch.source,trainingProvider=batch.provider,fallback=batch.fallback,message=batch.message;
 const ratings=buildRatings(games);
 const baseline=sport==="NFL"?23:sport==="NHL"?3:sport==="MLB"?4.5:112;
 const hfa=sport==="NFL"?2.2:sport==="NHL"?.18:sport==="MLB"?.25:2.2;
 const projection=projectMatchup(ratings,away,home,baseline,hfa);
 if(!projection)return NextResponse.json({error:"No model coverage for matchup",state:"model",trainingDataState,trainingProvider,fallback,message},{status:404});
 return NextResponse.json({model:"rounders-v1",trainingDataState,trainingProvider,fallback,message,sampleGames:Math.floor(games.length/2),projection});
}
