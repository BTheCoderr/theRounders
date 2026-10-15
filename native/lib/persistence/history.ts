import {createHash} from "node:crypto";
import type {TeamGame} from "../ratings";
import {uniqueCompletedGames} from "../powerRatings";
import {getEspnResults} from "../results/espn";

export type Sport="NBA"|"NFL"|"NHL"|"MLB";
const validSports=new Set(["NBA","NFL","NHL","MLB"]);
const origin=()=>process.env.SUPABASE_URL||process.env.NEXT_PUBLIC_SUPABASE_URL;
const serviceKey=()=>process.env.SUPABASE_SERVICE_ROLE_KEY;
export const archiveConfigured=()=>Boolean(origin()&&serviceKey());

async function rest(resource:string,options:RequestInit={}):Promise<Response>{
 const url=origin(),key=serviceKey();
 if(!url||!key)throw new Error("Historical database is not configured");
 const response=await fetch(url+"/rest/v1/"+resource,{
  ...options,cache:"no-store",
  headers:{apikey:key,Authorization:"Bearer "+key,"Content-Type":"application/json",...options.headers}
 });
 if(!response.ok)throw new Error("Historical database returned HTTP "+response.status);
 return response;
}
export async function claimSharedAiQuota(identityHash:string):Promise<boolean>{
 if(!/^[0-9a-f]{64}$/.test(identityHash))return false;
 try{
  const response=await rest("rpc/rounders_claim_ai_quota",{
   method:"POST",body:JSON.stringify({p_identity:identityHash})
  });
  return (await response.json())===true;
 }catch{return false} // Fail closed. No billable LLM call without shared DB quota.
}
export type ArchiveResult={games:TeamGame[];provider:string;dataState:"external";sampleGames:number;newestGame:string};
type ArchiveRow={
 occurred_at:string;home:string;away:string;home_score:number;away_score:number;neutral:boolean;
};
export async function readArchivedGames(sport:Sport,maxPages=5):Promise<ArchiveResult|null>{
 if(!archiveConfigured())return null;
 const rows:ArchiveRow[]=[];
 for(let page=0;page<maxPages;page++){
  const start=page*1000,end=start+999;
  const res=await rest("rounders_games?select=occurred_at,home,away,home_score,away_score,neutral&sport=eq."+
   encodeURIComponent(sport)+"&order=occurred_at.desc&limit=1000&offset="+start);
  const batch=await res.json() as ArchiveRow[];
  if(!Array.isArray(batch))throw new Error("Invalid archive response");
  rows.push(...batch);
  if(batch.length<1000)break;
 }
 if(rows.length<10)return null;
 const games=rows.flatMap(g=>{
  if(!g.home||!g.away||!Number.isFinite(g.home_score)||!Number.isFinite(g.away_score))return [];
  const date=g.occurred_at;
  const home={date,team:g.home,opponent:g.away,teamScore:g.home_score,opponentScore:g.away_score,location:(g.neutral?"neutral":"home") as TeamGame["location"]};
  const away={date,team:g.away,opponent:g.home,teamScore:g.away_score,opponentScore:g.home_score,location:(g.neutral?"neutral":"away") as TeamGame["location"]};
  return [home,away];
 });
 if(games.length<20)return null;
 return {games,provider:"Rounders archive (ESPN completed games)",dataState:"external",sampleGames:games.length/2,newestGame:rows[0].occurred_at};
}
export async function getTrainingGames(sport:Sport):Promise<{games:TeamGame[];provider:string;source:"external"|"simulated";fallback:boolean;sampleGames:number;message:string}>{
 try{
  const archive=await readArchivedGames(sport);
  if(archive)return {games:archive.games,provider:archive.provider,source:"external",fallback:false,sampleGames:archive.sampleGames,
   message:"Stored historical results; incomplete archives must not be treated as season-complete."};
 }catch{/* Use external scoreboard before controlled fallback */}
 try{
  const result=await getEspnResults(sport);
  return {games:result.games,provider:result.provider,source:result.source,fallback:false,sampleGames:result.games.length/2,
   message:"External scoreboard response; full-season completeness not established."};
 }catch{
  const {demoHistory}=await import("../demoHistory");
  const games=demoHistory(sport);
  return {games,provider:"controlled-demo",source:"simulated",fallback:true,sampleGames:games.length/2,
   message:"SIMULATED FALLBACK. Do not interpret as current real sports results."};
 }
}
export async function archiveEspnSeason(sport:Sport):Promise<number>{
 if(!validSports.has(sport))throw new Error("Invalid sport");
 const batch=await getEspnResults(sport);
 const games=uniqueCompletedGames(batch.games);
 let count=0;
 for(let i=0;i<games.length;i+=100){
  const data=games.slice(i,i+100).map(g=>({
   source:"espn-scoreboard",source_event_id:createHash("sha256").update([sport,g.date,g.home,g.away].join("|")).digest("hex"),
   sport,season:Number(g.date.slice(0,4)),occurred_at:g.date,
   home:g.home,away:g.away,home_score:g.homeScore,away_score:g.awayScore,neutral:g.neutral
  }));
  await rest("rounders_games?on_conflict=source,sport,source_event_id",{
   method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},body:JSON.stringify(data)
  });
  count+=data.length;
 }
 return count;
}
export async function recordIngestion(sport:Sport,count:number,status:"ok"|"error",detail:string){
 await rest("rounders_ingestion_runs",{
  method:"POST",headers:{Prefer:"return=minimal"},body:JSON.stringify({
   sport,source:"espn-scoreboard",games_seen:count,status,detail:detail.slice(0,180)
  })
 });
}

export async function recordModelEvaluation(sport:Sport){
 const data=await getTrainingGames(sport);
 const {computePowerBoard,holdoutMarginEvaluation}=await import("../powerRatings");
 const today=new Date();
 const board=computePowerBoard(data.games,sport,today);
 const holdout=holdoutMarginEvaluation(data.games,sport,today);
 await rest("rounders_model_runs?on_conflict=sport,model_version,run_day",{
  method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},
  body:JSON.stringify({
   sport,model_version:board.model,run_day:today.toISOString().slice(0,10),as_of:today.toISOString(),
   data_source:data.provider+(data.fallback?" (SIMULATED)":""),
   training_games:board.games,evaluated_games:holdout.evaluatedGames,
   model_mae:holdout.modelMAE,baseline_mae:holdout.homeBaselineMAE,
   beats_baseline:holdout.beatsBaseline
  })
 });
 return {trained:board.games,evaluated:holdout.evaluatedGames};
}


export async function saveComparison(sport:Sport):Promise<{evaluated:number;weeks:number;state:"external"|"simulated"}>{
 const result=await getTrainingGames(sport);
 const {compareWalkForward}=await import("../walkForward");
 const evaluated=compareWalkForward(result.games,sport,new Date(),52);
 const today=new Date();
 await rest("rounders_model_comparisons?on_conflict=sport,method,run_day",{
  method:"POST",
  headers:{Prefer:"resolution=merge-duplicates,return=minimal"},
  body:JSON.stringify({
   sport,method:evaluated.method,run_day:today.toISOString().slice(0,10),
   data_source:result.provider,data_state:result.source,historical_games:evaluated.totalHistoricalGames,
   evaluated_games:evaluated.evaluatedGames,evaluated_weeks:evaluated.evaluatedWeeks,
   seasons:evaluated.historySeasons,metrics:evaluated.models,best_model:evaluated.bestByMAE,
   beats_baseline:evaluated.betterThanBaseline,warning:evaluated.warning
  })
 });
 return {evaluated:evaluated.evaluatedGames,weeks:evaluated.evaluatedWeeks,state:result.source};
}
export async function readComparison(sport:Sport){
 if(!archiveConfigured())return null;
 const res=await rest("rounders_model_comparisons?select=sport,method,run_day,data_source,data_state,historical_games,evaluated_games,evaluated_weeks,seasons,metrics,best_model,beats_baseline,warning&sport=eq."+
  encodeURIComponent(sport)+"&order=run_day.desc&limit=1");
 const result=await res.json() as Array<{
  sport:Sport;method:string;run_day:string;data_source:string;data_state:"external"|"simulated";
  historical_games:number;evaluated_games:number;evaluated_weeks:number;seasons:number[];
  metrics:Array<{model:string;games:number;mae:number|null;winnerAccuracy:number|null;meanBias:number|null}>;
  best_model:string|null;beats_baseline:boolean|null;warning:string;
 }>;
 return result[0]||null;
}
