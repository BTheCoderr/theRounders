import {NextResponse} from "next/server";
import {isEngineSport} from "../../../lib/engine/models";
import {loadRatings} from "../../../lib/persistence/pageData";

export const dynamic="force-dynamic";
/** Ratings table for one sport: rating, offense, defense, schedule strength, record, projection and movement. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 const data=await loadRatings(sport);
 if(!data.ready){const {status,...body}=data;return NextResponse.json({sport,...body},{status,headers:{"Cache-Control":"no-store"}});}
 return NextResponse.json(data,{headers:{"Cache-Control":"public, max-age=0, s-maxage=900, stale-while-revalidate=300","Netlify-Vary":"query"}});
}
