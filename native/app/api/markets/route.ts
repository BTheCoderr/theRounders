import {NextRequest,NextResponse} from "next/server";
import {ALL_SPORTS,type Sport} from "../../../lib/sports";
import {archiveConfigured} from "../../../lib/persistence/history";
import {storedQuotes} from "../../../lib/persistence/odds";

/**
 * Line shop served from stored odds snapshots. Visitors never trigger a paid provider call:
 * the scheduled odds job is the only caller of The Odds API (centralized cache + budget).
 * "fresh" means the newest capture is inside the polling window (6h, 15 min near tip-off).
 */
const FRESH_MS=6.5*3600000;
const SPORTS=new Set<string>(ALL_SPORTS);
export const dynamic="force-dynamic";
export async function GET(req:NextRequest){
 const sport=(req.nextUrl.searchParams.get("sport")||"NBA").toUpperCase();
 if(!SPORTS.has(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 const unavailable=(error:string)=>NextResponse.json({provider:"the-odds-api",mode:"unavailable",fallback:false,fresh:false,ageMs:null,markets:[],error},{status:503,headers:{"Cache-Control":"no-store"}});
 if(!archiveConfigured())return unavailable("Market storage is not configured");
 try{
  const {quotes,capturedAt}=await storedQuotes(sport as Sport);
  const markets=quotes.filter(q=>q.state==="live"&&Date.parse(q.startTime)>Date.now());
  if(!markets.length)return unavailable("No stored sportsbook prices for this sport yet");
  const ageMs=capturedAt?Date.now()-Date.parse(capturedAt):null;
  return NextResponse.json({provider:"the-odds-api",mode:"live",fallback:false,fresh:ageMs!==null&&ageMs>=0&&ageMs<=FRESH_MS,ageMs,capturedAt,markets},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=120","Netlify-Vary":"query"}});
 }catch{return unavailable("Market feed unavailable")}
}
