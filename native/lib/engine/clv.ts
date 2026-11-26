/**
 * Market comparison and closing line value (CLV), from LOCKED pregame picks and captured
 * opening/closing consensus lines. Spreads are home spreads (home -3.5 means home favored).
 * Only games with both lines and a final score count; nothing is imputed.
 */
export type MarketRow={projectedMargin:number;homeWinProbability:number;
 openSpread:number|null;closeSpread:number|null;closeHomeProb:number|null;
 finalHome:number|null;finalAway:number|null};
export type MarketReport={
 games:number;withClose:number;
 clv:{games:number;avgPoints:number|null;beatClose:number|null};
 atsClose:{games:number;wins:number;losses:number;pushes:number;winRate:number|null};
 brier:{games:number;model:number|null;market:number|null};
};
const r=(x:number,d=3)=>Number(x.toFixed(d));
export function marketReport(rows:readonly MarketRow[]):MarketReport{
 let clvN=0,clvSum=0,clvPos=0,bN=0,bm=0,bk=0,withClose=0;
 const ats={games:0,wins:0,losses:0,pushes:0};
 for(const g of rows){
  const modelSpread=-g.projectedMargin;
  const final=g.finalHome!==null&&g.finalAway!==null?g.finalHome-g.finalAway:null;
  if(g.closeSpread!==null)withClose++;
  // CLV: which side the model takes against the OPENING line, and how far the market moved its way by the close.
  if(g.openSpread!==null&&g.closeSpread!==null&&modelSpread!==g.openSpread){
   const side=modelSpread<g.openSpread?1:-1;            // 1 = model likes home vs the open
   const pts=side*(g.openSpread-g.closeSpread);
   clvN++;clvSum+=pts;if(pts>0)clvPos++;
  }
  // Against the closing number: model side vs close, graded on the final.
  if(g.closeSpread!==null&&final!==null&&modelSpread!==g.closeSpread){
   const side=modelSpread<g.closeSpread?1:-1;const cover=final+g.closeSpread;
   ats.games++;
   if(cover===0)ats.pushes++;else if((cover>0)===(side===1))ats.wins++;else ats.losses++;
  }
  // Probability quality vs the market's vig-free closing probability, same games.
  if(g.closeHomeProb!==null&&final!==null&&final!==0){
   const y=final>0?1:0;bN++;bm+=(g.homeWinProbability-y)**2;bk+=(g.closeHomeProb-y)**2;
  }
 }
 const decided=ats.wins+ats.losses;
 return {games:rows.length,withClose,
  clv:{games:clvN,avgPoints:clvN?r(clvSum/clvN,2):null,beatClose:clvN?r(clvPos/clvN):null},
  atsClose:{...ats,winRate:decided?r(ats.wins/decided):null},
  brier:{games:bN,model:bN?r(bm/bN,4):null,market:bN?r(bk/bN,4):null}};
}
