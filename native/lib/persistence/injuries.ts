import {rest} from "./history";
import {recordUsage,spendState} from "./odds";
import {latestBacktest} from "./predictions";
import {BDL_BASE,fetchAllPages,injuriesPath,parseInjuries,type RawInjury} from "../providers/balldontlie";
import {decideSpend,spendPolicy} from "../providers/spend";
import {INJURY_MODEL,INJURY_REVISION,injuryAdjustment,nbaImpacts,nflImpacts,type BoxRow,type Impact,type Listed} from "../engine/injuries";
import {sigmaFromSummary} from "../engine/calibration";
import {winProbability} from "../engine/metrics";
import {teamKey} from "../engine/market";
import {seasonFor} from "../sports";

type Sport2="NBA"|"NFL";
const HOUR=3600000;

/** One budgeted BALLDONTLIE request (requests count as 1 credit against the monthly ceiling). */
async function bdl<T>(path:string,params:Record<string,string|string[]>={}):Promise<T>{
 const policy=spendPolicy("balldontlie");
 if(!policy.enabled)throw new Error("BALLDONTLIE disabled");
 const d=decideSpend(policy,await spendState("balldontlie"),1);
 if(!d.allow){await recordUsage("balldontlie",0,null,1);throw new Error("BALLDONTLIE budget: "+d.reason);}
 const qs=new URLSearchParams();
 for(const [k,v] of Object.entries(params))for(const x of Array.isArray(v)?v:[v])qs.append(k,x);
 const res=await fetch(`${BDL_BASE}${path}${qs.size?"?"+qs:""}`,{headers:{Authorization:process.env.BALLDONTLIE_API_KEY!},cache:"no-store",signal:AbortSignal.timeout(10000)});
 await recordUsage("balldontlie",1,null);
 if(res.status===401||res.status===403)throw new Error("BALLDONTLIE plan does not include "+path);
 if(!res.ok)throw new Error("BALLDONTLIE HTTP "+res.status);
 return await res.json() as T;
}

/** Fetch the current injury report and log changes. A player stays "current" while last_seen_at is fresh. */
export async function refreshInjuries(sport:Sport2,now=new Date()){
 if(!spendPolicy("balldontlie").enabled)return {sport,skipped:"disabled"};
 const teams=new Map<string,string>();
 if(sport==="NBA"){
  const t=await bdl<{data:Array<{id:number;full_name:string}>}>("/v1/teams");
  for(const x of t.data)teams.set(String(x.id),x.full_name);
 }
 const raw=await fetchAllPages<RawInjury>(cursor=>bdl(injuriesPath(sport),{per_page:"100",...(cursor?{cursor}:{})}));
 const list=parseInjuries(raw,teams);
 const seen=now.toISOString();
 const rows=list.map(i=>({sport,provider:"balldontlie",player_id:i.playerId,player_name:i.name,team:i.team,position:i.position,
  status:i.status,description:i.description,return_date:i.returnDate,reported_at:i.reportedAt,report_hash:i.hash,last_seen_at:seen}));
 for(let k=0;k<rows.length;k+=200)
  await rest("rounders_injury_reports?on_conflict=sport,provider,player_id,report_hash",{method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},body:JSON.stringify(rows.slice(k,k+200))});
 return {sport,listed:rows.length};
}
async function currentInjuries(sport:Sport2,now:Date):Promise<Listed[]>{
 const since=new Date(now.getTime()-2*HOUR).toISOString();
 const r=await rest(`rounders_injury_reports?select=player_id,player_name,team,status,reported_at,first_seen_at&sport=eq.${sport}&last_seen_at=gte.${encodeURIComponent(since)}&order=first_seen_at.desc&limit=2000`);
 const rows=await r.json() as Array<{player_id:string;player_name:string;team:string|null;status:string;reported_at:string|null;first_seen_at:string}>;
 const out=new Map<string,Listed>();
 for(const x of rows)if(x.team&&!out.has(x.player_id))out.set(x.player_id,{playerId:x.player_id,name:x.player_name,team:x.team,status:x.status,reportedAt:x.reported_at??x.first_seen_at});
 return [...out.values()];
}

type BoxScore={game?:{id?:number|string};id?:number|string;date?:string;home_team?:{full_name?:string;players?:BoxPlayer[]};visitor_team?:{full_name?:string;players?:BoxPlayer[]}};
type BoxPlayer={player?:{id?:number|string;first_name?:string;last_name?:string};min?:string|number;plus_minus?:number|null};
const minutes=(m:string|number|undefined)=>{if(typeof m==="number")return m;if(!m)return 0;const [a,b]=String(m).split(":");return Number(a)+(Number(b)||0)/60;};
/** Parse NBA box scores into per-player game rows. Players without minutes are skipped (DNP). */
export function parseBoxScores(scores:BoxScore[],date:string){
 const out:Array<{game_id:string;player_id:string;player_name:string;team:string;minutes:number;plus_minus:number|null;game_date:string}>=[];
 for(const s of scores){
  const gid=String(s.game?.id??s.id??"");if(!gid)continue;
  for(const side of [s.home_team,s.visitor_team]){
   if(!side?.full_name)continue;
   for(const p of side.players||[]){
    const id=p.player?.id,min=minutes(p.min);
    if(id===undefined||!(min>0))continue;
    out.push({game_id:gid,player_id:String(id),player_name:[p.player?.first_name,p.player?.last_name].filter(Boolean).join(" "),
     team:side.full_name,minutes:Number(min.toFixed(2)),plus_minus:Number.isFinite(p.plus_minus)?p.plus_minus!:null,game_date:date});
   }
  }
 }
 return out;
}

/** NBA: pull box scores for days not yet stored (time-boxed), then recompute impacts. NFL: starting-QB prior. */
export async function refreshImpacts(sport:Sport2,now=new Date(),budgetMs=20000){
 if(!spendPolicy("balldontlie").enabled)return {sport,skipped:"disabled"};
 const started=Date.now(),season=seasonFor(sport,now.getTime());
 if(sport==="NBA"){
  const have=await (await rest(`rounders_player_games?select=game_date&sport=eq.NBA&game_date=gte.${season}-10-01&order=game_date.desc&limit=1`)).json() as Array<{game_date:string}>;
  let day=have[0]?new Date(Date.parse(have[0].game_date)+86400000):new Date(Date.UTC(season,9,15));
  const yesterday=new Date(now.getTime()-86400000);let days=0;
  while(day<=yesterday&&Date.now()-started<budgetMs){
   const date=day.toISOString().slice(0,10);
   const res=await bdl<{data:BoxScore[]}>("/v1/box_scores",{date});
   const rows=parseBoxScores(res.data||[],date).map(r=>({...r,sport:"NBA",provider:"balldontlie"}));
   if(rows.length)await rest("rounders_player_games?on_conflict=sport,provider,game_id,player_id",{method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},body:JSON.stringify(rows)});
   day=new Date(day.getTime()+86400000);days++;
  }
  const games=await (await rest(`rounders_player_games?select=player_id,player_name,team,minutes,plus_minus&sport=eq.NBA&game_date=gte.${season}-10-01&limit=50000`)).json() as Array<{player_id:string;player_name:string;team:string;minutes:number;plus_minus:number|null}>;
  const box:BoxRow[]=games.filter(g=>g.plus_minus!==null).map(g=>({playerId:g.player_id,name:g.player_name,team:g.team,minutes:Number(g.minutes),plusMinus:Number(g.plus_minus)}));
  return {sport,days,...await saveImpacts(sport,season,nbaImpacts(box))};
 }
 const stats=await fetchAllPages<{player?:{id:number;first_name?:string;last_name?:string;position_abbreviation?:string;team?:{full_name?:string}};passing_attempts?:number;games_played?:number}>(
  cursor=>bdl("/nfl/v1/season_stats",{season:String(season),per_page:"100",...(cursor?{cursor}:{})}));
 const qbs=stats.filter(s=>s.player?.position_abbreviation==="QB"&&s.player.team?.full_name).map(s=>({playerId:String(s.player!.id),
  name:[s.player!.first_name,s.player!.last_name].filter(Boolean).join(" "),team:s.player!.team!.full_name!,attempts:s.passing_attempts??0,games:s.games_played??0}));
 return {sport,...await saveImpacts(sport,season,nflImpacts(qbs))};
}
async function saveImpacts(sport:Sport2,season:number,impacts:Impact[]){
 const rows=impacts.map(i=>({sport,provider:"balldontlie",player_id:i.playerId,player_name:i.name,team:i.team,season,games:i.games,
  minutes_share:i.mpg?Number((i.mpg/48).toFixed(3)):null,impact:i.impact,method:i.method,computed_at:new Date().toISOString()}));
 for(let k=0;k<rows.length;k+=500)
  await rest("rounders_player_impact?on_conflict=sport,provider,player_id,season",{method:"POST",headers:{Prefer:"resolution=merge-duplicates,return=minimal"},body:JSON.stringify(rows.slice(k,k+500))});
 return {players:rows.length};
}

/**
 * Injury-adjusted v4 forecasts for upcoming locked power-v2 picks. The locked pick is never
 * touched: each forecast is a new timestamped row, written only when the adjustment changes.
 */
export async function createAdjustedForecasts(sport:Sport2,now=new Date()){
 if(!spendPolicy("balldontlie").enabled)return {sport,skipped:"disabled"};
 const until=new Date(now.getTime()+30*HOUR).toISOString(),from=new Date(now.getTime()+10*60000).toISOString();
 const base=await (await rest(`rounders_predictions?select=id,provider_event_id,starts_at,home,away,projected_margin&sport=eq.${sport}&model_id=eq.power-v2&grade_status=eq.pending&starts_at=gte.${encodeURIComponent(from)}&starts_at=lt.${encodeURIComponent(until)}&limit=300`)).json() as Array<{id:number;provider_event_id:string;starts_at:string;home:string;away:string;projected_margin:number}>;
 if(!base.length)return {sport,games:0,written:0};
 const season=seasonFor(sport,now.getTime());
 const [listed,impRows,prev,bt]=await Promise.all([
  currentInjuries(sport,now),
  rest(`rounders_player_impact?select=player_id,player_name,team,games,impact,method&sport=eq.${sport}&season=eq.${season}&limit=5000`).then(r=>r.json() as Promise<Array<{player_id:string;player_name:string;team:string;games:number;impact:number;method:string}>>),
  rest(`rounders_adjusted_forecasts?select=provider_event_id,injury_adjustment,forecast_at&sport=eq.${sport}&provider_event_id=in.(${base.map(b=>b.provider_event_id).join(",")})&order=forecast_at.desc`).then(r=>r.json() as Promise<Array<{provider_event_id:string;injury_adjustment:number}>>),
  latestBacktest(sport).catch(()=>null)]);
 if(!impRows.length)return {sport,games:base.length,written:0,skipped:"no player impacts yet"};
 const impacts=new Map<string,Impact>(impRows.map(i=>[i.player_id,{playerId:i.player_id,name:i.player_name,team:i.team,games:i.games,mpg:0,impact:Number(i.impact),method:i.method}]));
 const last=new Map<string,number>();for(const p of prev)if(!last.has(p.provider_event_id))last.set(p.provider_event_id,Number(p.injury_adjustment));
 const pm=bt?.models.find(m=>m.model==="power-v2");
 const sigma=typeof pm?.sigma==="number"&&pm.sigma>0?pm.sigma:sigmaFromSummary(sport,pm?.summary);
 // Injury feeds and ESPN may spell teams differently: compare normalized names.
 const norm=(l:Listed)=>({...l,team:teamKey(l.team)});
 const listedN=listed.map(norm);
 const rows=[];
 for(const g of base){
  const adj=injuryAdjustment(teamKey(g.home),teamKey(g.away),listedN,impacts);
  if(last.has(g.provider_event_id)&&Math.abs(last.get(g.provider_event_id)!-adj.net)<0.25)continue;
  if(!last.has(g.provider_event_id)&&adj.players.length===0)continue;   // nothing to adjust: v4 equals v2
  const margin=Number(g.projected_margin)+adj.net;
  rows.push({sport,provider_event_id:g.provider_event_id,base_prediction_id:g.id,model_id:INJURY_MODEL,model_version:INJURY_REVISION,
   forecast_at:now.toISOString(),starts_at:g.starts_at,base_margin:g.projected_margin,injury_adjustment:adj.net,projected_margin:Number(margin.toFixed(2)),
   home_win_probability:Number(winProbability(margin,sigma).toFixed(4)),inputs:{home:adj.home,away:adj.away,players:adj.players,sigma}});
 }
 if(rows.length)await rest("rounders_adjusted_forecasts",{method:"POST",headers:{Prefer:"return=minimal"},body:JSON.stringify(rows)});
 return {sport,games:base.length,written:rows.length};
}
/** Grade adjusted forecasts whose locked base pick has been graded. */
export async function gradeAdjustedForecasts(now=new Date()){
 const r=await rest(`rounders_adjusted_forecasts?select=id,base_prediction_id,projected_margin,home_win_probability&graded_at=is.null&starts_at=lt.${encodeURIComponent(new Date(now.getTime()-90*60000).toISOString())}&limit=500`);
 const pending=await r.json() as Array<{id:number;base_prediction_id:number;projected_margin:number;home_win_probability:number}>;
 if(!pending.length)return {graded:0};
 const ids=[...new Set(pending.map(p=>p.base_prediction_id))];
 const finals=new Map<number,{h:number;a:number}>();
 for(let i=0;i<ids.length;i+=100){
  const b=await (await rest(`rounders_predictions?select=id,final_home,final_away&id=in.(${ids.slice(i,i+100).join(",")})&grade_status=eq.graded`)).json() as Array<{id:number;final_home:number;final_away:number}>;
  for(const x of b)finals.set(x.id,{h:x.final_home,a:x.final_away});
 }
 let graded=0;
 for(const p of pending){
  const f=finals.get(p.base_prediction_id);if(!f)continue;
  const m=f.h-f.a,decided=m!==0,y=m>0?1:0;
  await rest(`rounders_adjusted_forecasts?id=eq.${p.id}&graded_at=is.null`,{method:"PATCH",headers:{Prefer:"return=minimal"},body:JSON.stringify({
   final_home:f.h,final_away:f.a,winner_correct:decided?(p.home_win_probability>=0.5)===(y===1):null,
   brier:decided?Number(((p.home_win_probability-y)**2).toFixed(5)):null,margin_error:Number((p.projected_margin-m).toFixed(2)),graded_at:now.toISOString()})});
  graded++;
 }
 return {graded};
}
