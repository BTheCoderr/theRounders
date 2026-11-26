import {NextResponse} from "next/server";
import {isSport} from "../../../lib/sports";
import {loadHistory} from "../../../lib/persistence/pageData";

export const dynamic="force-dynamic";
/** Final regular-season Power Index ratings for any archived season. */
export async function GET(req:Request){
 const url=new URL(req.url),sport=(url.searchParams.get("sport")||"NBA").toUpperCase();
 if(!isSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 const data=await loadHistory(sport,Number(url.searchParams.get("season"))||null);
 if(!data.ready){const {status,...body}=data;return NextResponse.json(body,{status,headers:{"Cache-Control":status===200?"public, max-age=0, s-maxage=600":"no-store","Netlify-Vary":"query"}});}
 return NextResponse.json(data,{headers:{"Cache-Control":"public, max-age=0, s-maxage=3600, stale-while-revalidate=600","Netlify-Vary":"query"}});
}
