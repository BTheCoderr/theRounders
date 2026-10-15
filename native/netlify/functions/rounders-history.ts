import {refreshHistoricalArchive,recordIngestion,recordModelEvaluation,saveComparison,type Sport} from "../../lib/persistence/history";

/** Netlify Scheduled Function. Runs only on published deploys, every six hours at minute 0 UTC. */
export default async function handler(_req:Request):Promise<Response>{
 const summary:Array<{sport:Sport;games:number;ok:boolean}>=[];
 for(const sport of ["NBA","NFL","NHL","MLB"] as Sport[]){
  try{
   const result=await refreshHistoricalArchive(sport);
   const count=result.games;
   await recordIngestion(sport,count,"ok","Imported months: "+(result.months.join(",")||"already up to date"));
   await recordModelEvaluation(sport);
   await saveComparison(sport);
   summary.push({sport,games:count,ok:true});
  }catch(error){
   // Do not log service keys or full payloads.
   const message=error instanceof Error?error.message:"Import failed";
   try{await recordIngestion(sport,0,"error",message)}catch{}
   summary.push({sport,games:0,ok:false});
  }
 }
 console.log("Rounders scheduled history refresh",JSON.stringify(summary));
 return new Response(JSON.stringify({ok:summary.every(x=>x.ok),results:summary}),{
  headers:{"content-type":"application/json"}
 });
}
export const config={schedule:"0 */6 * * *"};
