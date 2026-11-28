/**
 * Head-to-head scorecard on the SAME games: each model's locked pick graded straight up,
 * against the closing spread (the last line captured before start) and by Brier score.
 * Only games where every compared model has a graded pick and a closing line count.
 */
export type ScoreRow={eventId:string;projectedMargin:number;homeWinProbability:number;finalHome:number;finalAway:number;closeSpreadHome:number|null};
export type ModelScore={games:number;su:{wins:number;losses:number;winRate:number|null};
 ats:{wins:number;losses:number;pushes:number;winRate:number|null};brier:number|null;mae:number|null};
const r=(x:number,d=3)=>Number(x.toFixed(d));
export function scoreModel(rows:readonly ScoreRow[]):ModelScore{
 let sw=0,sl=0,aw=0,al=0,ap=0,b=0,bn=0,e=0;
 for(const g of rows){
  const m=g.finalHome-g.finalAway;e+=Math.abs(g.projectedMargin-m);
  if(m!==0){const y=m>0?1:0;b+=(g.homeWinProbability-y)**2;bn++;if((g.homeWinProbability>=0.5)===(y===1))sw++;else sl++;}
  if(g.closeSpreadHome!==null){
   const edge=g.projectedMargin+g.closeSpreadHome;
   if(edge!==0){const cover=m+g.closeSpreadHome;if(cover===0)ap++;else if((cover>0)===(edge>0))aw++;else al++;}
  }
 }
 return {games:rows.length,su:{wins:sw,losses:sl,winRate:sw+sl?r(sw/(sw+sl)):null},
  ats:{wins:aw,losses:al,pushes:ap,winRate:aw+al?r(aw/(aw+al)):null},brier:bn?r(b/bn,4):null,mae:rows.length?r(e/rows.length,2):null};
}
/** Keep only events every model has, so the comparison is like for like. */
export function sameGames<T extends {eventId:string}>(byModel:Record<string,readonly T[]>):Record<string,T[]>{
 const keys=Object.keys(byModel);if(!keys.length)return {};
 const common=keys.map(k=>new Set(byModel[k].map(x=>x.eventId))).reduce((a,b)=>new Set([...a].filter(x=>b.has(x))));
 return Object.fromEntries(keys.map(k=>[k,byModel[k].filter(x=>common.has(x.eventId))]));
}
