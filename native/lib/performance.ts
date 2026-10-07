import type {MarketName} from "./contracts";

export type ProjectionSnapshot={
 id:string;eventId:string;sport:string;away:string;home:string;createdAt:string;
 modelVersion:string;trainingProvider:string;trainingDataState:string;
 projectedAway:number;projectedHome:number;fairSpreadHome:number;
 homeWinProbability:number;confidence:number;
 market?:{market:MarketName;selection:string;line?:number;price:number;book:string;capturedAt:string};
 closing?:{line?:number;price:number;book:string;capturedAt:string};
 final?:{awayScore:number;homeScore:number;completedAt:string};
};

export type GradedProjection={
 snapshot:ProjectionSnapshot;winnerCorrect?:boolean;absoluteMarginError?:number;
 atsResult?:"win"|"loss"|"push";clvPoints?:number;clvPrice?:number;
 brier?:number;
};

export function gradeProjection(s:ProjectionSnapshot):GradedProjection{
 const out:GradedProjection={snapshot:s}; if(!s.final)return out;
 const actualHomeWin=s.final.homeScore>s.final.awayScore?1:0;
 const predicted=s.homeWinProbability/100;
 out.winnerCorrect=(predicted>=.5)===Boolean(actualHomeWin);
 out.brier=(predicted-actualHomeWin)**2;
 const actualMargin=s.final.homeScore-s.final.awayScore;
 const projectedMargin=s.projectedHome-s.projectedAway;
 out.absoluteMarginError=Math.abs(projectedMargin-actualMargin);
 if(s.market?.market==="spread"&&s.market.line!==undefined){
   const selectionIsHome=s.market.selection===s.home;
   const coverMargin=selectionIsHome?actualMargin+s.market.line:-actualMargin+s.market.line;
   out.atsResult=coverMargin>0?"win":coverMargin<0?"loss":"push";
 }
 if(s.market?.market==="spread"&&s.market.line!==undefined&&s.closing?.line!==undefined){
   const home=s.market.selection===s.home;
   out.clvPoints=home?s.market.line-s.closing.line:s.closing.line-s.market.line;
 }
 if(s.market&&s.closing)out.clvPrice=s.market.price-s.closing.price;
 return out;
}

export function summarize(grades:GradedProjection[]){
 const completed=grades.filter(g=>g.snapshot.final);
 const decided=completed.filter(g=>g.winnerCorrect!==undefined);
 const ats=completed.filter(g=>g.atsResult&&g.atsResult!=="push");
 const clv=completed.filter(g=>g.clvPoints!==undefined);
 const avg=(xs:number[])=>xs.length?xs.reduce((a,b)=>a+b,0)/xs.length:null;
 return{
  completed:completed.length,
  winnerAccuracy:decided.length?decided.filter(g=>g.winnerCorrect).length/decided.length*100:null,
  meanAbsoluteMarginError:avg(completed.flatMap(g=>g.absoluteMarginError===undefined?[]:[g.absoluteMarginError])),
  brierScore:avg(completed.flatMap(g=>g.brier===undefined?[]:[g.brier])),
  atsRecord:{wins:ats.filter(g=>g.atsResult==="win").length,losses:ats.filter(g=>g.atsResult==="loss").length,pushes:completed.filter(g=>g.atsResult==="push").length},
  atsWinRate:ats.length?ats.filter(g=>g.atsResult==="win").length/ats.length*100:null,
  averageClvPoints:avg(clv.map(g=>g.clvPoints!))
 };
}

export function calibrationBuckets(grades:GradedProjection[]){
 const buckets=[50,55,60,65,70,75,80,85,90,95];
 return buckets.map(low=>{const rows=grades.filter(g=>g.snapshot.final&&g.snapshot.homeWinProbability>=low&&g.snapshot.homeWinProbability<low+5);
 const wins=rows.filter(g=>g.snapshot.final!.homeScore>g.snapshot.final!.awayScore).length;
 return{range:`${low}-${low+4}%`,predictions:rows.length,actualWinRate:rows.length?wins/rows.length*100:null};});
}
