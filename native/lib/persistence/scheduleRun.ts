import {refreshHistoricalArchive,recordIngestion,recordModelEvaluation,saveComparison,type Sport} from "./history";

export async function runScheduledSport(sport:Sport):Promise<Response>{
 let imported=0;
 let months:string[]=[];
 let status:"ok"|"error"="ok";
 let detail="";
 try{
  const result=await refreshHistoricalArchive(sport);
  imported=result.games;
  months=result.months;
  detail="Imported months: "+(months.join(",")||"already up to date");
 }catch(error){
  status="error";
  detail=error instanceof Error?error.message:"Import failed";
 }
 try{await recordIngestion(sport,imported,status,detail)}catch{/* log only */}
 // Model scorecards should still update even when the external provider fails.
 // They label simulated fallback explicitly; no misrepresentation of data.
 const stages:Record<string,"ok"|"error">={import:status};
 for(const [step,run] of [
  ["scorecard",()=>recordModelEvaluation(sport)],
  ["comparison",()=>saveComparison(sport)]
 ] as Array<[string,()=>Promise<unknown>]>){
  try{await run();stages[step]="ok"}catch{stages[step]="error"}
 }
 const ok=Object.values(stages).every(s=>s==="ok");
 const summary={sport,ok,imported,months,stages};
 console.log("rounders history scheduled",JSON.stringify(summary));
 return Response.json(summary,{status:ok?200:503});
}
