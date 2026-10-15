import {NextResponse} from "next/server";
import {getTrainingGames} from "../../../lib/persistence/history";
import {computePowerBoard,holdoutMarginEvaluation,type Sport} from "../../../lib/powerRatings";

export const dynamic="force-dynamic";
const SPORTS=new Set(["NBA","NFL","NHL","MLB"]);

export async function GET(req:Request){
  const sport=(new URL(req.url).searchParams.get("sport")||"NBA").toUpperCase();
  if(!SPORTS.has(sport))return NextResponse.json({error:"Unsupported sport"},{status:400});
  const batch=await getTrainingGames(sport as Sport);
  const games=batch.games, dataState=batch.source,provider=batch.provider,fallback=batch.fallback;
  const warning=batch.message;
  const now=new Date();
  const board=computePowerBoard(games,sport as Sport,now);
  const evaluation=holdoutMarginEvaluation(games,sport as Sport,now);
  const medianGames=board.rankings.length
    ?[...board.rankings].sort((a,b)=>a.games-b.games)[Math.floor(board.rankings.length/2)].games:0;
  const coverage=board.rankings.length>=20&&medianGames>=5?"substantial":"limited";
  const notes=[
    ...(warning?[warning]:[]),
    ...(coverage==="limited"?["Limited league coverage or sparse team schedules. Rankings may be unreliable."]:[]),
    "Ratings are a preview, not Kenneth Massey's official rankings; no model calibration or proven betting advantage."
  ];
  return NextResponse.json({
    ...board,dataState,provider,fallback,coverage,medianGames,
    evaluation,notes,
    retrievedAt:now.toISOString(),
  },{headers:{"Cache-Control":"public, max-age=0, s-maxage=600, stale-while-revalidate=120"}});
}
