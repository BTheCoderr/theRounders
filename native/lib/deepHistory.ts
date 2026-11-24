import {SPORT_CONFIG,type Sport} from "./sports.ts";

/** Months (YYYYMM) of the model window, newest first, matching the regular importer. */
function windowKeys(now:Date,count:number):Set<string>{
 const out=new Set<string>();
 for(let i=0;i<count;i++){const d=new Date(Date.UTC(now.getUTCFullYear(),now.getUTCMonth()-i,1));out.add(String(d.getUTCFullYear())+String(d.getUTCMonth()+1).padStart(2,"0"));}
 return out;
}
export const DEEP_HISTORY_FLOOR=1980;
const ymKey=(y:number,m:number)=>String(y)+String(m).padStart(2,"0");
export function deepHistoryPlan(sport:Sport,now:Date,done:Map<string,number>){
 const cfg=SPORT_CONFIG[sport];
 const window=windowKeys(now,cfg.historyMonths);
 let emptyRun=0;
 for(let d=new Date(Date.UTC(now.getUTCFullYear(),now.getUTCMonth()-cfg.historyMonths,1));d.getUTCFullYear()>=DEEP_HISTORY_FLOOR;d=new Date(Date.UTC(d.getUTCFullYear(),d.getUTCMonth()-1,1))){
  const y=d.getUTCFullYear(),m=d.getUTCMonth()+1,key=ymKey(y,m);
  if(window.has(key)||!cfg.seasonMonths.includes(m))continue;
  const n=done.get(key);
  if(n===undefined)return {next:key,floorReached:false};
  emptyRun=n>0?0:emptyRun+1;
  if(emptyRun>=12)return {next:null,floorReached:true};
 }
 return {next:null,floorReached:false};
}
