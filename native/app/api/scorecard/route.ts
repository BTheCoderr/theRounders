import {NextResponse} from "next/server";
import {MODEL_LABELS,isEngineSport,type ModelId} from "../../../lib/engine/models";
import {sameGames,scoreModel,type ScoreRow} from "../../../lib/engine/scorecard";
import {archiveConfigured} from "../../../lib/persistence/history";
import {listGradedPredictions} from "../../../lib/persistence/predictions";
import {latestLines} from "../../../lib/persistence/odds";

export const dynamic="force-dynamic";
const MODELS:ModelId[]=["power-v2","blend-v1"];
/** power-v2 vs the market blend on the same graded games, plus the market line itself as a reference. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 if(!archiveConfigured())return NextResponse.json({sport,ready:false,reason:"Storage is not configured."},{status:503});
 try{
  const graded=await Promise.all(MODELS.map(m=>listGradedPredictions(sport,m,2000)));
  const ids=[...new Set(graded.flat().map(p=>p.provider_event_id))];
  const lines=await latestLines(sport,ids);
  const num=(v:unknown)=>v===null||v===undefined?null:Number.isFinite(Number(v))?Number(v):null;
  const rows=Object.fromEntries(MODELS.map((m,i)=>[m,graded[i].filter(p=>p.final_home!==null&&p.final_away!==null&&lines.has(p.provider_event_id)).map(p=>({
   eventId:p.provider_event_id,projectedMargin:p.projected_margin,homeWinProbability:p.home_win_probability,finalHome:p.final_home!,finalAway:p.final_away!,
   closeSpreadHome:num(lines.get(p.provider_event_id)!.spread_home)} as ScoreRow))]));
  const same=sameGames(rows);
  // The market itself: home margin = -close spread, probability = vig-free close.
  const ref=same["power-v2"]?.map(g=>{const l=lines.get(g.eventId)!;const s=num(l.spread_home),p=num(l.home_win_prob);
   return s===null||p===null?null:{...g,projectedMargin:-s,homeWinProbability:p};}).filter((x):x is ScoreRow=>x!==null)??[];
  return NextResponse.json({sport,ready:true,games:same["power-v2"]?.length??0,
   models:MODELS.map(m=>({model:m,label:MODEL_LABELS[m],...scoreModel(same[m]||[])})),
   market:{label:"Closing line (reference)",...scoreModel(ref),ats:null},
   notes:["Same games only: each model's locked pick, graded after the final.","Against the spread uses the last line captured before start; 52.4% breaks even at -110.","Small samples are noise."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=300","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({sport,ready:false,reason:"Scorecard is temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
