import type {TeamGame} from "./ratings";
import {uniqueCompletedGames,type Sport} from "./powerRatings.ts";

export type SeasonCoverage={season:number;games:number;teams:number;approximateShare:number;status:"partial"|"candidate";};
export type DataQuality={
 sport:Sport;provider:string;state:"external"|"simulated";games:number;
 expectedTeams:number;observedTeams:number;
 seasons:SeasonCoverage[];seasonsWithNearFullCounts:number;
 researchReady:boolean;warnings:string[];
};
/**
 * An audit, not certification. The thresholds are deliberately approximate;
 * playoff/preseason contamination and source omissions must still be ruled out.
 * Calendar-year archives differ from league season boundaries.
 */
const expected:Record<Sport,{teams:number;regularSeasonGames:number}>={
 NBA:{teams:30,regularSeasonGames:1230},
 NFL:{teams:32,regularSeasonGames:272},
 NHL:{teams:32,regularSeasonGames:1312},
 MLB:{teams:30,regularSeasonGames:2430}
};
export function seasonYear(sport:Sport,date:string):number{
 const year=Number(date.slice(0,4)),month=Number(date.slice(5,7));
 if(!Number.isInteger(year)||month<1||month>12)throw new Error("Invalid date");
 return sport==="MLB"?year:month>=7?year:year-1;
}
export function auditGameHistory(rows:TeamGame[],sport:Sport,provider="unknown",state:"external"|"simulated"="external",asOf=new Date()):DataQuality{
 const cfg=expected[sport];if(!cfg)throw new Error("Unsupported sport");
 const games=uniqueCompletedGames(rows,asOf);
 const bySeason=new Map<number,{games:number;teams:Set<string>}>();
 for(const g of games){
  const season=seasonYear(sport,g.date);
  const record=bySeason.get(season)||{games:0,teams:new Set<string>()};
  record.games++;record.teams.add(g.home);record.teams.add(g.away);bySeason.set(season,record);
 }
 const allTeams=new Set(games.flatMap(g=>[g.home,g.away]));
 const seasons=[...bySeason].sort(([a],[b])=>a-b).map(([season,detail])=>{
  const approximateShare=Number((detail.games/cfg.regularSeasonGames).toFixed(3));
  const status:SeasonCoverage["status"]=approximateShare>=0.9&&detail.teams.size===cfg.teams?"candidate":"partial";
  return {season,games:detail.games,teams:detail.teams.size,approximateShare,status};
 });
 const nearFull=seasons.filter(s=>s.status==="candidate").length;
 const warnings:string[]=[];
 if(state==="simulated")warnings.push("SIMULATED results are never eligible for public model-validation claims.");
 if(!games.length)warnings.push("No completed, deduplicated games available.");
 if(nearFull<5)warnings.push("Fewer than five near-complete season candidates. Research dataset is insufficient for locked cross-season claims.");
 if(seasons.some(s=>s.teams>cfg.teams))warnings.push("More team names than the normal professional league size; verify preseason/all-star entries and stable team identity.");
 if(seasons.some(s=>s.approximateShare<0.9))warnings.push("One or more seasons have substantially fewer games than normal regular-season schedules.");
 warnings.push("Season counts are approximate and include any playoffs/preseason in the source. Even a candidate season is NOT independently certified complete.");
 return {sport,provider,state,games:games.length,expectedTeams:cfg.teams,observedTeams:allTeams.size,
  seasons,seasonsWithNearFullCounts:nearFull,
  researchReady:state==="external"&&nearFull>=5&&!seasons.some(s=>s.teams>cfg.teams),
  warnings};
}
