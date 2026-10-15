import {NextResponse} from "next/server";
import {buildRatings,projectMatchup} from "../../../../lib/ratings";
import {demoHistory} from "../../../../lib/demoHistory";
import {getEspnResults} from "../../../../lib/results/espn";
import {createEvidence,explainFromModel,readResponseText,ANALYST_INSTRUCTIONS} from "../../../../lib/aiInsights";

export const dynamic="force-dynamic";
const SPORTS=new Set(["NBA","NFL","NHL","MLB"]);
// A best-effort per-instance guard. Set a provider-level quota / durable rate limit
// before turning on billable public AI in production; serverless instances do not share this map.
const recent=new Map<string,{count:number;reset:number}>();
function limited(ip:string):boolean{
  const now=Date.now();
  if(recent.size>2000)for(const [key,v] of recent)if(v.reset<=now)recent.delete(key);
  const item=recent.get(ip);
  if(!item||item.reset<=now){recent.set(ip,{count:1,reset:now+900_000});return false}
  item.count++;
  return item.count>8;
}
function json(data:unknown,status=200){
  return NextResponse.json(data,{status,headers:{"Cache-Control":"no-store"}});
}
export async function POST(req:Request){
  const length=Number(req.headers.get("content-length")||0);
  if(length>2500)return json({error:"Request too large"},413);
  let body:unknown;
  try{
    const raw=await req.text();
    if(raw.length>2500)return json({error:"Request too large"},413);
    body=JSON.parse(raw);
  }catch{return json({error:"Expected a JSON request"},400)}
  if(!body||typeof body!=="object")return json({error:"Invalid request"},400);
  const {sport,away,home,question} = body as Record<string,unknown>;
  if(typeof sport!=="string"||!SPORTS.has(sport)||
    typeof away!=="string"||typeof home!=="string"||
    !away.trim()||!home.trim()||away===home||away.length>80||home.length>80||
    typeof question!=="string"||question.trim().length<3||question.length>240){
      return json({error:"A valid sport, matchup and question (3-240 characters) are required"},400);
  }
  const id=req.headers.get("x-nf-client-connection-ip")||req.headers.get("x-forwarded-for")?.split(",")[0]?.trim()||"anonymous";
  if(limited(id))return json({error:"Analysis request limit reached. Please try again later."},429);
  let games=demoHistory(sport);
  let source:{trainingDataState:"external"|"simulated";trainingProvider:string;fallback:boolean;sampleGames:number}={
    trainingDataState:"simulated",trainingProvider:"controlled-demo",fallback:true,sampleGames:Math.floor(games.length/2)
  };
  try{
    const batch=await getEspnResults(sport);
    games=batch.games;
    source={trainingDataState:batch.source,trainingProvider:batch.provider,fallback:false,sampleGames:Math.floor(games.length/2)};
  }catch{/* Clearly labeled controlled fallback; never call simulated games live. */}
  const ratings=buildRatings(games);
  const baseline=sport==="NFL"?23:sport==="NHL"?3:sport==="MLB"?4.5:112;
  const hfa=sport==="NFL"?2.2:sport==="NHL"?.18:sport==="MLB"?.25:2.2;
  const projection=projectMatchup(ratings,away,home,baseline,hfa);
  if(!projection)return json({error:"No model coverage for this matchup",source},404);
  const evidence=createEvidence(sport,projection,source);
  const summary=explainFromModel(evidence,question);
  const enabled=process.env.ROUNDERS_AI_ENABLED==="true"&&Boolean(process.env.OPENAI_API_KEY);
  if(!enabled)return json({mode:"model-summary",answer:summary,evidence,notice:"LLM commentary is disabled; this is a statistical model explanation, not generative AI."});

  try{
    const response=await fetch("https://api.openai.com/v1/responses",{
      method:"POST",
      headers:{"Authorization":`Bearer ${process.env.OPENAI_API_KEY}`,"Content-Type":"application/json"},
      body:JSON.stringify({
        model:process.env.ROUNDERS_AI_MODEL||"gpt-4.1-mini",
        instructions:ANALYST_INSTRUCTIONS,
        input:JSON.stringify({userQuestion:question,evidence,modelSummary:summary}),
        max_output_tokens:360,
        store:false
      }),
      signal:AbortSignal.timeout(8500)
    });
    if(response.ok){
      const data=await response.json();
      const answer=readResponseText(data);
      if(answer)return json({mode:"ai",answer,evidence,notice:"AI commentary grounded in the displayed statistical model. Not a guarantee."});
    }
  }catch{/* Provider unavailable; use transparent model-only summary. */}
  return json({mode:"model-summary",answer:summary,evidence,notice:"AI provider unavailable; showing model-only summary."});
}
