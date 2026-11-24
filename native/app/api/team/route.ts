import {NextResponse} from "next/server";
import {MODEL_LABELS,isEngineSport} from "../../../lib/engine/models";
import {championFor} from "../../../lib/engine/promotion";
import {ratingHistory,teamGames} from "../../../lib/engine/ratingsTable";
import {seasonOf} from "../../../lib/engine/backtest";
import {ratingsWithProjections} from "../../../lib/persistence/ratingsData";
import {listTeamPredictions} from "../../../lib/persistence/predictions";
import {archiveConfigured} from "../../../lib/persistence/history";

export const dynamic="force-dynamic";
/**
 * One team: ratings row, weekly rating history, this season's results with the
 * pick we stored before each game, and upcoming games (winner + probability only,
 * the free tier; spreads and totals stay on the plan-gated predictions API).
 */
export async function GET(req:Request){
 const url=new URL(req.url);
 const sport=(url.searchParams.get("sport")||"").toUpperCase(),slug=(url.searchParams.get("team")||"").toLowerCase();
 if(!isEngineSport(sport)||!/^[a-z0-9-]{2,60}$/.test(slug))return NextResponse.json({error:"Valid sport and team are required"},{status:400});
 if(!archiveConfigured())return NextResponse.json({ready:false,reason:"Ratings storage is not configured."},{status:503});
 try{
  const now=new Date();
  const {games,table}=await ratingsWithProjections(sport,now);
  const row=table.rows.find(r=>r.slug===slug);
  if(!row)return NextResponse.json({ready:false,reason:"Team not found."},{status:404});
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
  return NextResponse.json({ready:true,sport,season,team:row,teams:table.rows.length,homeAdvantage:table.homeAdvantage,
   model,modelLabel:MODEL_LABELS[model],history:ratingHistory(games,sport,row.team,now),results,upcoming},
   {headers:{"Cache-Control":"public, max-age=0, s-maxage=900, stale-while-revalidate=300","Netlify-Vary":"query"}});
 }catch{
  return NextResponse.json({ready:false,reason:"Team data is temporarily unavailable."},{status:503,headers:{"Cache-Control":"no-store"}});
 }
}
