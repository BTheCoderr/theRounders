import {cache} from "react";
import {MODEL_LABELS,type EngineSport} from "../engine/models";
import {championFor} from "../engine/promotion";
import {buildRatingsTable,ratingHistory,teamGames,type RatingsTable} from "../engine/ratingsTable";
import {seasonOf} from "../engine/backtest";
import {uniqueCompletedGames} from "../powerRatings";
import {seasonEndDate} from "../sports";
import {ratingsWithProjections} from "./ratingsData";
import {listTeamPredictions} from "./predictions";
import {archiveConfigured,availableSeasons,getSeasonGames} from "./history";

/**
 * One source for the ratings, team and history data, shared by the JSON APIs and the
 * server-rendered pages, so search engines and the app see exactly the same numbers.
 * Each loader returns {ready:false,reason,status} instead of throwing.
 */
export type NotReady={ready:false;reason:string;status:number;sport?:string;season?:number;seasons?:number[]};
const notReady=(reason:string,status:number,extra:Partial<NotReady>={}):NotReady=>({ready:false,reason,status,...extra});

export type RatingsPayload=RatingsTable&{ready:true;provider:string;model:string;notes:string[]};
export const loadRatings=cache(async(sport:EngineSport):Promise<RatingsPayload|NotReady>=>{
 if(!archiveConfigured())return notReady("Ratings storage is not configured.",503,{sport});
 try{
  const {provider,games,table}=await ratingsWithProjections(sport,new Date());
  if(games.length<50||!table.rows.length)return notReady("This sport's history is still loading. Check back soon.",503,{sport});
  return {...table,ready:true,provider,model:"power-v2",
   notes:["Rounders Power Index ratings from verified regular-season results. These are not Kenneth Massey's ratings.",
    "Offense and defense are per game, better than average against an average opponent. Projected records add each remaining game's win probability."]};
 }catch{return notReady("Ratings are temporarily unavailable.",503,{sport});}
});

export const loadTeam=cache(async(sport:EngineSport,slug:string)=>{
 if(!/^[a-z0-9-]{2,60}$/.test(slug))return notReady("Valid sport and team are required",400);
 if(!archiveConfigured())return notReady("Ratings storage is not configured.",503);
 try{
  const now=new Date();
  const {games,table}=await ratingsWithProjections(sport,now);
  const row=table.rows.find(r=>r.slug===slug);
  if(!row)return notReady("Team not found.",404);
  const model=championFor(sport);
  const stored=await listTeamPredictions(sport,model,row.team).catch(()=>[]);
  const season=table.season;
  const byKey=new Map(stored.map(p=>[p.starts_at.slice(0,10)+"|"+(p.home===row.team?p.away:p.home),p]));
  const rankOf=new Map(table.rows.map(r=>[r.team,r.rank]));
  const results=teamGames(games.filter(g=>seasonOf(g.date,sport)===season),row.team).map(g=>{
   const p=byKey.get(g.date.slice(0,10)+"|"+g.opponent)??null;
   const pickedTeam=p?p.projected_winner===row.team:null;
   return {...g,opponentRank:rankOf.get(g.opponent)??null,
    pick:p&&p.grade_status==="graded"?{winner:p.projected_winner,teamWinProbability:p.home===row.team?p.home_win_probability:1-p.home_win_probability,
     correct:p.winner_correct,predictedAt:p.predicted_at,pickedTeam}:null};
  }).reverse();
  const upcoming=stored.filter(p=>p.grade_status==="pending"&&Date.parse(p.starts_at)>now.getTime()).map(p=>({
   startsAt:p.starts_at,opponent:p.home===row.team?p.away:p.home,home:p.home===row.team,neutral:p.neutral,
   opponentRank:rankOf.get(p.home===row.team?p.away:p.home)??null,
   winner:p.projected_winner,teamWinProbability:p.home===row.team?p.home_win_probability:1-p.home_win_probability,predictedAt:p.predicted_at}));
  return {ready:true as const,sport,season,team:row,teams:table.rows.length,homeAdvantage:table.homeAdvantage,
   model,modelLabel:MODEL_LABELS[model],history:ratingHistory(games,sport,row.team,now),results,upcoming};
 }catch{return notReady("Team data is temporarily unavailable.",503);}
});
export type TeamPayload=Exclude<Awaited<ReturnType<typeof loadTeam>>,NotReady>;

export type HistoryPayload=RatingsTable&{ready:true;seasons:number[];historical:true;notes:string[]};
export const loadHistory=cache(async(sport:EngineSport,asked?:number|null):Promise<HistoryPayload|NotReady>=>{
 if(!archiveConfigured())return notReady("Storage is not configured.",503,{sport});
 try{
  const seasons=await availableSeasons(sport);
  if(!seasons.length)return notReady("History for this sport is still loading.",200,{sport,seasons});
  // Default to the latest completed season.
  const finished=seasons.filter(y=>seasonEndDate(sport,y).getTime()<Date.now());
  const season=asked&&seasons.includes(asked)?asked:(finished[0]??seasons[0]);
  const games=uniqueCompletedGames(await getSeasonGames(sport,season),new Date());
  if(games.length<20)return notReady("Not enough games archived for this season yet.",200,{sport,season,seasons});
  const table=buildRatingsTable(games,sport,new Date(Date.parse(games[games.length-1].date)+86400000));
  return {...table,rows:table.rows.map(r=>({...r,change:null})),ready:true,seasons,historical:true,
   notes:["Final regular-season Power Index ratings, computed from that season's results only. Team names as they were at the time."]};
 }catch{return notReady("History is temporarily unavailable.",503,{sport});}
});
