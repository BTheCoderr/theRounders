import {NextResponse} from "next/server";
import {MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";
import {championFor} from "../../../lib/engine/promotion";
import {listGradedPredictions,summarizeStored} from "../../../lib/persistence/predictions";
import {archiveConfigured} from "../../../lib/persistence/history";
import {ALL_SPORTS} from "../../../lib/sports";

export const dynamic="force-dynamic";
/** "Strong pick" = the model gives the side at least this win probability. Fixed in advance. */
const STRONG=0.7;
/** Public ledger: every graded pick the live model stored before its game, newest first. */
export async function GET(req:Request){
 const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
 if(sport==="ALL")return overall();
 if(!isEngineSport(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
 if(!archiveConfigured())return NextResponse.json({sport,ready:false,reason:"Storage is not configured."},{status:503});
 try{
  const model=championFor(sport);
  const rows=await listGradedPredictions(sport,model,1000);
  return NextResponse.json({sport,ready:true,model,modelLabel:MODEL_LABELS[model],summary:summarizeStored(rows),
   picks:rows.slice(0,400).map(r=>({eventId:r.provider_event_id,startsAt:r.starts_at,predictedAt:r.predicted_at,home:r.home,away:r.away,
    winner:r.projected_winner,probability:r.projected_winner===r.home?r.home_win_probability:1-r.home_win_probability,
    projectedSpreadHome:Number((-r.projected_margin).toFixed(1)),projectedTotal:r.projected_total,
    final:{home:r.final_home,away:r.final_away},correct:r.winner_correct,marginError:r.margin_error,modelVersion:r.model_version})),
   notes:["Each pick was stored before its game started and is never edited. Spreads and totals are shown after the final only.",
    "Ties are excluded from accuracy. No result here implies future profitability."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=300","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({sport,ready:false,reason:"Track record is temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}

/** All-sports straight-up record of each sport's live champion. Ties excluded. */
async function overall(){
 if(!archiveConfigured())return NextResponse.json({sport:"ALL",ready:false,reason:"Storage is not configured."},{status:503});
 try{
  const bySport=await Promise.all(ALL_SPORTS.filter(isEngineSport).map(async s=>{
   const model=championFor(s);const rows=await listGradedPredictions(s,model,5000);
   const wins=rows.filter(r=>r.winner_correct===true).length,losses=rows.filter(r=>r.winner_correct===false).length;
   const strong=rows.filter(r=>Math.max(r.home_win_probability,1-r.home_win_probability)>=STRONG);
   return {sport:s,model,wins,losses,winRate:wins+losses?Number((wins/(wins+losses)).toFixed(4)):null,
    strongWins:strong.filter(r=>r.winner_correct===true).length,strongLosses:strong.filter(r=>r.winner_correct===false).length};
  }));
  const wins=bySport.reduce((a,x)=>a+x.wins,0),losses=bySport.reduce((a,x)=>a+x.losses,0);
  const sw=bySport.reduce((a,x)=>a+x.strongWins,0),sl=bySport.reduce((a,x)=>a+x.strongLosses,0);
  return NextResponse.json({sport:"ALL",ready:true,wins,losses,winRate:wins+losses?Number((wins/(wins+losses)).toFixed(4)):null,
   strong:{threshold:STRONG,wins:sw,losses:sl,winRate:sw+sl?Number((sw/(sw+sl)).toFixed(4)):null},bySport,
   notes:["Straight-up winners of locked pregame picks from each sport's live model. Ties excluded.","Strong picks are the subset where the model gave the side 70% or more; every pick is still shown in the full record.","No result here implies future profitability."]},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=300","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({sport:"ALL",ready:false,reason:"Track record is temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
