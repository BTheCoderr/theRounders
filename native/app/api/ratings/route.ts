import {NextResponse} from "next/server";
import {SPORT_CONFIG,isSport} from "../../../lib/sports";
import {buildRatings,projectMatchup} from "../../../lib/ratings";
import {getTrainingGames} from "../../../lib/persistence/history";
export const dynamic="force-dynamic";
export async function GET(req:Request){
 const {searchParams}=new URL(req.url),sport=(searchParams.get("sport")||"NBA").toUpperCase(),away=searchParams.get("away"),home=searchParams.get("home");
 if(!isSport(sport)||!away||!home||away.length>80||home.length>80||away===home)return NextResponse.json({error:"Valid sport, away and home are required"},{status:400});
 const batch=await getTrainingGames(sport);
 const games=batch.games,trainingDataState=batch.source,trainingProvider=batch.provider,fallback=batch.fallback,message=batch.message;
 const ratings=buildRatings(games);
 const baseline=SPORT_CONFIG[sport].v1Baseline;
 const hfa=SPORT_CONFIG[sport].homeAdvantage;
 const projection=projectMatchup(ratings,away,home,baseline,hfa);
 if(!projection)return NextResponse.json({error:"No model coverage for matchup",state:"model",trainingDataState,trainingProvider,fallback,message},{status:404});
 return NextResponse.json({model:"rounders-v1",trainingDataState,trainingProvider,fallback,message,sampleGames:Math.floor(games.length/2),projection});
}
