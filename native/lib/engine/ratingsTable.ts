import {computePowerBoard,type CompletedGame} from "../powerRatings.ts";
import type {TeamGame} from "../ratings";
import {fitTotals} from "./totals.ts";
import {seasonOf} from "./backtest.ts";
import type {EngineSport} from "./models.ts";

/**
 * Full ratings table (Massey-style layout) from the live Power Index:
 *  rating   points better than an average team on a neutral site (schedule-adjusted, recency-weighted)
 *  offense  points scored above an average team against an average defense
 *  defense  points allowed below average (positive = better defense)
 *  sos      average rating of this season's opponents
 *  change   rank movement versus seven days earlier
 * All numbers come from completed games before `asOf`.
 */
export type RatingRow={
 rank:number;change:number|null;team:string;slug:string;
 wins:number;losses:number;ties:number;games:number;
 rating:number;offense:number|null;defense:number|null;sos:number|null;
 last10:{wins:number;losses:number};streak:string;
 pointsFor:number|null;pointsAgainst:number|null;
};
export type RatingsTable={sport:EngineSport;season:number;asOf:string;games:number;homeAdvantage:number;leaguePoints:number|null;rows:RatingRow[]};

export const teamSlug=(name:string)=>name.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");
const r1=(x:number)=>Number(x.toFixed(1)),r2=(x:number)=>Number(x.toFixed(2));
const DAY=86400000;
const homeRows=(games:CompletedGame[]):TeamGame[]=>games.map(g=>({date:g.date,team:g.home,opponent:g.away,teamScore:g.homeScore,opponentScore:g.awayScore,location:g.neutral?"neutral" as const:"home" as const}));

export function teamGames(games:CompletedGame[],team:string){
 return games.filter(g=>g.home===team||g.away===team).map(g=>{
  const home=g.home===team;
  const pf=home?g.homeScore:g.awayScore,pa=home?g.awayScore:g.homeScore;
  return {date:g.date,opponent:home?g.away:g.home,home,neutral:g.neutral,pf,pa,result:pf>pa?"W" as const:pf<pa?"L" as const:"T" as const};
 });
}

export function buildRatingsTable(history:CompletedGame[],sport:EngineSport,asOf:Date):RatingsTable{
 const past=history.filter(g=>Date.parse(g.date)<asOf.getTime());
 const season=past.length?seasonOf(past[past.length-1].date):seasonOf(asOf.toISOString());
 const current=past.filter(g=>seasonOf(g.date)===season);
 const board=computePowerBoard(homeRows(past),sport,new Date(asOf.getTime()-1));
 const weekAgo=new Date(asOf.getTime()-7*DAY);
 const before=computePowerBoard(homeRows(past.filter(g=>Date.parse(g.date)<weekAgo.getTime())),sport,weekAgo);
 const prevRank=new Map(before.rankings.map(x=>[x.team,x.rank]));
 const totals=fitTotals(past,sport,asOf);
 const rating=new Map(board.rankings.map(x=>[x.team,x.rating]));
 const active=new Set(current.flatMap(g=>[g.home,g.away]));
 const ranked=board.rankings.filter(x=>active.has(x.team));
 const rows:RatingRow[]=ranked.map((x,i)=>{
  const own=teamGames(current,x.team);
  const wins=own.filter(g=>g.result==="W").length,losses=own.filter(g=>g.result==="L").length,ties=own.length-wins-losses;
  const opp=own.map(g=>rating.get(g.opponent)).filter((v):v is number=>v!==undefined);
  const last=own.slice(-10);
  let streak="";
  if(own.length){const k=own[own.length-1].result;let n=0;for(let j=own.length-1;j>=0&&own[j].result===k;j--)n++;streak=k+n;}
  const prev=prevRank.get(x.team);
  // Ranks among this season's teams only, so movement compares like with like.
  const prevAmongActive=prev===undefined?null:before.rankings.filter(y=>active.has(y.team)&&y.rank<prev).length+1;
  const off=totals.offense.get(x.team),def=totals.defense.get(x.team);
  return {rank:i+1,change:prevAmongActive===null||before.games===board.games?null:prevAmongActive-(i+1),
   team:x.team,slug:teamSlug(x.team),wins,losses,ties,games:own.length,
   rating:r2(x.rating),offense:off===undefined?null:r1(off),defense:def===undefined?null:r1(-def),
   sos:opp.length?r2(opp.reduce((s,v)=>s+v,0)/opp.length):null,
   last10:{wins:last.filter(g=>g.result==="W").length,losses:last.filter(g=>g.result==="L").length},streak,
   pointsFor:own.length?r1(own.reduce((s,g)=>s+g.pf,0)/own.length):null,
   pointsAgainst:own.length?r1(own.reduce((s,g)=>s+g.pa,0)/own.length):null};
 });
 return {sport,season,asOf:asOf.toISOString(),games:current.length,homeAdvantage:board.parameters.homeAdvantage,
  leaguePoints:totals.games?r1(totals.mu):null,rows};
}

/** Weekly Power Index history for one team this season (rating and rank each Monday, plus today). */
export function ratingHistory(history:CompletedGame[],sport:EngineSport,team:string,asOf:Date){
 const past=history.filter(g=>Date.parse(g.date)<asOf.getTime());
 if(!past.length)return [];
 const season=seasonOf(past[past.length-1].date);
 const current=past.filter(g=>seasonOf(g.date)===season);
 if(!current.length)return [];
 const start=Date.parse(current[0].date);
 const points:number[]=[];
 const d=new Date(start+7*DAY);
 let t=Date.UTC(d.getUTCFullYear(),d.getUTCMonth(),d.getUTCDate())-((d.getUTCDay()+6)%7)*DAY;
 for(;t<asOf.getTime();t+=7*DAY)points.push(t);
 points.push(asOf.getTime());
 const out:Array<{date:string;rating:number;rank:number}>=[];
 for(const p of points.slice(-30)){
  const games=past.filter(g=>Date.parse(g.date)<p);
  const active=new Set(current.filter(g=>Date.parse(g.date)<p).flatMap(g=>[g.home,g.away]));
  const board=computePowerBoard(homeRows(games),sport,new Date(p-1));
  const ranked=board.rankings.filter(x=>active.has(x.team));
  const i=ranked.findIndex(x=>x.team===team);
  if(i>=0)out.push({date:new Date(p).toISOString(),rating:r2(ranked[i].rating),rank:i+1});
 }
 return out;
}
