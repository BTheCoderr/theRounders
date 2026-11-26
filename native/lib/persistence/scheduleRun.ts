import {refreshHistoricalArchive,recordIngestion,recordModelEvaluation,saveComparison,type Sport} from "./history";

/** Strictly bounded import job. No statistical model computation consumes this 30s budget. */
export async function runScheduledSport(sport:Sport):Promise<Response>{
 let imported=0,months:string[]=[],status:"ok"|"error"="ok",detail="";
 try{
  const result=await refreshHistoricalArchive(sport);
  imported=result.games;months=result.months;
  detail="Imported months: "+(months.join(",")||"already up to date");
 }catch(error){
  status="error";detail=error instanceof Error?error.message:"Import failed";
 }
 let receipt=true;
 try{await recordIngestion(sport,imported,status,detail)}
 catch{receipt=false;console.error("Rounders failed to record import receipt",sport)}
 const ok=status==="ok"&&receipt;
 const summary={sport,ok,imported,months,receipt,status,detail};
 console.log("rounders history scheduled",JSON.stringify(summary));
 return Response.json(summary,{status:ok?200:503});
}

/** Independent daily evaluation, only after the import jobs have had time to finish. */
export async function runScheduledEvaluation(sport:Sport):Promise<Response>{
 const results:Record<string,"ok"|"error">={};
 for(const [stage,task] of [
  ["scorecard",()=>recordModelEvaluation(sport)],
  ["comparison",()=>saveComparison(sport)]
 ] as Array<[string,()=>Promise<unknown>]>){
  try{await task();results[stage]="ok"}
  catch(error){
   results[stage]="error";
   console.error("Rounders daily model evaluation failed",sport,stage,
    error instanceof Error?error.message:"unknown error");
  }
 }
 const ok=Object.values(results).every(x=>x==="ok");
 console.log("rounders model evaluation",JSON.stringify({sport,ok,results}));
 return Response.json({sport,ok,results},{status:ok?200:503});
}

/** Shared wrapper: one bounded task per invocation, JSON receipt, 503 on failure. */
async function receipt(name:string,detail:Record<string,unknown>,task:()=>Promise<Record<string,unknown>>):Promise<Response>{
 try{
  const result=await task();
  console.log(name,JSON.stringify({...detail,ok:true,...result}));
  return Response.json({...detail,ok:true,...result});
 }catch(error){
  const message=error instanceof Error?error.message:"failed";
  console.error(name,JSON.stringify({...detail,ok:false,error:message}));
  return Response.json({...detail,ok:false,error:message},{status:503});
 }
}
/** Daily slate (basketball, hockey, baseball) or weekly slate (football): first immutable pregame snapshot per game and model. */
export async function runScheduledPredictions(sport:Sport):Promise<Response>{
 const {snapshotPredictions}=await import("./predictions");
 return receipt("rounders predictions",{sport},()=>snapshotPredictions(sport));
}
export async function runScheduledGrading():Promise<Response>{
 const {gradePendingPredictions}=await import("./predictions");
 const {gradeAdjustedForecasts}=await import("./injuries");
 return receipt("rounders grading",{},async()=>{
  const picks=await gradePendingPredictions();
  // v4 tables may not exist before migration 012; the locked picks still grade.
  const adjusted=await gradeAdjustedForecasts().catch(e=>({error:e instanceof Error?e.message:"failed"}));
  return {...picks,adjusted};
 });
}
/** Odds capture for every sport, within the polling policy and spend budget. */
export async function runScheduledOdds():Promise<Response>{
 const {captureOdds}=await import("./odds");
 const {ALL_SPORTS}=await import("../sports");
 return receipt("rounders odds",{},async()=>{
  const started=Date.now(),out:Record<string,unknown>={};
  for(const s of ALL_SPORTS){
   if(Date.now()-started>20000){out[s]="deferred";continue;}
   try{out[s]=await captureOdds(s);}catch(e){out[s]={error:e instanceof Error?e.message:"failed"};}
  }
  return out;
 });
}
/** Hourly: injury reports for NBA and NFL, then injury-adjusted v4 forecasts. */
export async function runScheduledInjuries():Promise<Response>{
 const {refreshInjuries,createAdjustedForecasts}=await import("./injuries");
 return receipt("rounders injuries",{},async()=>{
  const out:Record<string,unknown>={};
  for(const s of ["NBA","NFL"] as const){
   try{out[s]={report:await refreshInjuries(s),forecasts:await createAdjustedForecasts(s)};}
   catch(e){out[s]={error:e instanceof Error?e.message:"failed"};}
  }
  return out;
 });
}
/** Daily: player game logs and impact ratings. */
export async function runScheduledImpacts():Promise<Response>{
 const {refreshImpacts}=await import("./injuries");
 return receipt("rounders impacts",{},async()=>{
  const out:Record<string,unknown>={};
  for(const s of ["NBA","NFL"] as const){try{out[s]=await refreshImpacts(s,new Date(),s==="NBA"?18000:8000);}catch(e){out[s]={error:e instanceof Error?e.message:"failed"};}}
  return out;
 });
}
export async function runScheduledBacktest(sport:Sport):Promise<Response>{
 const {recordBacktest}=await import("./predictions");
 return receipt("rounders backtest",{sport},()=>recordBacktest(sport));
}
