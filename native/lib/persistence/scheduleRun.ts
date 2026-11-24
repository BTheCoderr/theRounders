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
/** Daily NBA slate / weekly NFL slate: first immutable pregame snapshot per game and model. */
export async function runScheduledPredictions(sport:"NBA"|"NFL"):Promise<Response>{
 const {snapshotPredictions}=await import("./predictions");
 return receipt("rounders predictions",{sport},()=>snapshotPredictions(sport));
}
export async function runScheduledGrading():Promise<Response>{
 const {gradePendingPredictions}=await import("./predictions");
 return receipt("rounders grading",{},()=>gradePendingPredictions());
}
export async function runScheduledBacktest(sport:"NBA"|"NFL"):Promise<Response>{
 const {recordBacktest}=await import("./predictions");
 return receipt("rounders backtest",{sport},()=>recordBacktest(sport));
}
