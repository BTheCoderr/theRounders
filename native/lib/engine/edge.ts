import type {Sport} from "../sports.ts";

/**
 * Edge picks: games where the locked model line disagrees with the market by at least a
 * fixed, pre-declared threshold. Thresholds are set in advance, not tuned on results.
 *  - Spread sports: edge = model margin - market margin (market margin = -home spread).
 *    Graded against the spread (closing line for finished games). Break-even at -110 is 52.4%.
 *  - NHL/MLB (puck/run lines are fixed at 1.5): edge = model home win probability minus the
 *    market's vig-free probability. Graded straight up; the market's average probability for
 *    the picked side is reported so the win rate can be read against what the price implied.
 */
export const EDGE_POINTS:Partial<Record<Sport,number>>={NBA:3,NFL:3,NCAAM:4,NCAAF:5};
export const EDGE_PROB:Partial<Record<Sport,number>>={NHL:0.06,MLB:0.06};
export const BREAK_EVEN_110=0.524;

export type EdgeInput={sport:Sport;eventId:string;startsAt:string;home:string;away:string;
 projectedMargin:number;homeWinProbability:number;
 marketSpreadHome:number|null;marketHomeProb:number|null;lineSource:string|null;lineAt:string|null;
 finalHome:number|null;finalAway:number|null};
export type EdgePick={eventId:string;startsAt:string;home:string;away:string;side:string;kind:"spread"|"moneyline";
 edge:number;modelLine:number;marketLine:number;lineSource:string|null;lineAt:string|null;
 result:"win"|"loss"|"push"|null;marketProbForSide:number|null};

const r=(x:number,d=1)=>Number(x.toFixed(d));
export function edgePick(g:EdgeInput):EdgePick|null{
 const pts=EDGE_POINTS[g.sport],prob=EDGE_PROB[g.sport];
 const final=g.finalHome!==null&&g.finalAway!==null?g.finalHome-g.finalAway:null;
 if(pts!==undefined){
  if(g.marketSpreadHome===null||!Number.isFinite(g.marketSpreadHome))return null;
  const edge=g.projectedMargin+g.marketSpreadHome;          // >0: model likes home vs the number
  if(Math.abs(edge)<pts)return null;
  const home=edge>0;
  let result:EdgePick["result"]=null;
  if(final!==null){const cover=final+g.marketSpreadHome;result=cover===0?"push":(cover>0)===home?"win":"loss";}
  return {eventId:g.eventId,startsAt:g.startsAt,home:g.home,away:g.away,side:home?g.home:g.away,kind:"spread",
   edge:r(Math.abs(edge)),modelLine:r(-g.projectedMargin),marketLine:g.marketSpreadHome,lineSource:g.lineSource,lineAt:g.lineAt,result,marketProbForSide:null};
 }
 if(prob!==undefined){
  if(g.marketHomeProb===null||!Number.isFinite(g.marketHomeProb))return null;
  const edge=g.homeWinProbability-g.marketHomeProb;
  if(Math.abs(edge)<prob)return null;
  const home=edge>0;
  const result:EdgePick["result"]=final===null?null:final===0?"push":(final>0)===home?"win":"loss";
  return {eventId:g.eventId,startsAt:g.startsAt,home:g.home,away:g.away,side:home?g.home:g.away,kind:"moneyline",
   edge:r(Math.abs(edge)*100),modelLine:r((home?g.homeWinProbability:1-g.homeWinProbability)*100),
   marketLine:r((home?g.marketHomeProb:1-g.marketHomeProb)*100),lineSource:g.lineSource,lineAt:g.lineAt,result,
   marketProbForSide:r(home?g.marketHomeProb:1-g.marketHomeProb,4)};
 }
 return null;
}
export type EdgeRecord={picks:number;wins:number;losses:number;pushes:number;winRate:number|null;breakEven:number|null};
export function edgeRecord(picks:readonly EdgePick[]):EdgeRecord{
 const done=picks.filter(p=>p.result!==null);
 const wins=done.filter(p=>p.result==="win").length,losses=done.filter(p=>p.result==="loss").length,pushes=done.filter(p=>p.result==="push").length;
 const ml=done.filter(p=>p.kind==="moneyline"&&p.result!=="push"&&p.marketProbForSide!==null);
 const breakEven=!done.length?null:done.every(p=>p.kind==="spread")?BREAK_EVEN_110:ml.length?r(ml.reduce((s,p)=>s+p.marketProbForSide!,0)/ml.length,3):null;
 return {picks:done.length,wins,losses,pushes,winRate:wins+losses?r(wins/(wins+losses),3):null,breakEven};
}
