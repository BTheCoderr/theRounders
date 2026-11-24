import {uniqueCompletedGames} from "../powerRatings";
import {getVerifiedResearchGames,readTeamRegistry} from "./history";
import {fetchUpcoming} from "../results/espnSchedule";
import {latestBacktest} from "./predictions";
import {sigmaFromSummary} from "../engine/calibration";
import {addProjections,buildRatingsTable,type RatingsTable} from "../engine/ratingsTable";
import {seasonEndDate} from "../sports";
import type {EngineSport} from "../engine/models";

/** Completed, de-duplicated regular-season games from the verified archive. */
export async function verifiedHistory(sport:EngineSport,now=new Date()){
 const archive=await getVerifiedResearchGames(sport);
 return {provider:archive.provider,games:uniqueCompletedGames(archive.games,now)};
}
/** Ratings table plus projected final records when the season is in progress (schedule cached 6h). */
export async function ratingsWithProjections(sport:EngineSport,now=new Date()):Promise<{table:RatingsTable;provider:string;games:ReturnType<typeof uniqueCompletedGames>}>{
 const {provider,games}=await verifiedHistory(sport,now);
 const table=buildRatingsTable(games,sport,now);
 const end=seasonEndDate(sport,table.season);
 if(!(end.getTime()>now.getTime()))return {table,provider,games};
 try{
  const [schedule,registry,backtest]=await Promise.all([
   fetchUpcoming(sport,now,end,{revalidate:21600,maxRequests:45}),readTeamRegistry(sport),latestBacktest(sport).catch(()=>null)]);
  const remaining=schedule.map(g=>({home:registry.get(g.homeId)||g.home,away:registry.get(g.awayId)||g.away,neutral:g.neutral}));
  const power=backtest?.models.find(m=>m.model==="power-v2");
  const sigma=typeof power?.sigma==="number"&&power.sigma>0?power.sigma:sigmaFromSummary(sport,power?.summary);
  return {table:addProjections(table,remaining,sigma),provider,games};
 }catch{
  return {table,provider,games};   // ratings still render if the schedule feed is down
 }
}
