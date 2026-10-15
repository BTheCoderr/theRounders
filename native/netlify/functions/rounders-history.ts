import {archiveEspnSeason,recordIngestion,type Sport} from "../../lib/persistence/history";

/** Netlify Scheduled Function. Runs only on published deploys, daily at 11:00 UTC. */
export default async function handler(_req:Request):Promise<Response>{
 const summary:Array<{sport:Sport;games:number;ok:boolean}>=[];
 for(const sport of ["NBA","NFL","NHL","MLB"] as Sport[]){
  try{
   const count=await archiveEspnSeason(sport);
   await recordIngestion(sport,count,"ok","Current-year completed scoreboard import");
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
export const config={schedule:"0 11 * * *"};
