import type {CompletedGame} from "../powerRatings";
import type {EngineSport} from "./models";

/**
 * Rounders Totals v1: recency-weighted, ridge-regularized offense/defense scoring model.
 *   home points = mu + homeEdge/2 + off[home] + def[away]
 *   away points = mu - homeEdge/2 + off[away] + def[home]
 * `def` is points allowed above average (positive = weaker defense).
 * Fitted by Gauss-Seidel on weighted least squares; only games before `asOf` are used.
 */
export const TOTALS_MODEL="totals-v1";
const settings:Record<EngineSport,{halfLifeDays:number;ridge:number;homeEdge:number}>={
 NBA:{halfLifeDays:45,ridge:4,homeEdge:2.2},
 NFL:{halfLifeDays:90,ridge:2,homeEdge:2.2}
};
const DAY=86400000;
export type TotalsFit={
 mu:number;games:number;
 offense:Map<string,number>;defense:Map<string,number>;
 predict(home:string,away:string,neutral:boolean):{home:number;away:number;total:number}|null;
};
export function fitTotals(history:CompletedGame[],sport:EngineSport,asOf:Date):TotalsFit{
 const cfg=settings[sport],cutoff=asOf.getTime();
 const games=history.filter(g=>Date.parse(g.date)<cutoff);
 const teams=[...new Set(games.flatMap(g=>[g.home,g.away]))].sort();
 const idx=new Map(teams.map((t,i)=>[t,i]));
 const n=teams.length;
 type Obs={atk:number;dfn:number;side:number;pts:number;w:number};
 const obs:Obs[]=[];
 for(const g of games){
  const w=Math.pow(0.5,Math.max(0,(cutoff-Date.parse(g.date))/DAY)/cfg.halfLifeDays);
  const side=g.neutral?0:cfg.homeEdge/2;
  obs.push({atk:idx.get(g.home)!,dfn:idx.get(g.away)!,side,pts:g.homeScore,w});
  obs.push({atk:idx.get(g.away)!,dfn:idx.get(g.home)!,side:-side,pts:g.awayScore,w});
 }
 const off=new Array<number>(n).fill(0),def=new Array<number>(n).fill(0);
 let wsum=0,psum=0;
 for(const o of obs){wsum+=o.w;psum+=o.w*o.pts;}
 let mu=wsum?psum/wsum:0;
 for(let iter=0;iter<60&&obs.length;iter++){
  let mNum=0;
  for(const o of obs)mNum+=o.w*(o.pts-o.side-off[o.atk]-def[o.dfn]);
  mu=mNum/wsum;
  const offNum=new Array<number>(n).fill(0),offDen=new Array<number>(n).fill(cfg.ridge);
  for(const o of obs){offNum[o.atk]+=o.w*(o.pts-mu-o.side-def[o.dfn]);offDen[o.atk]+=o.w;}
  let delta=0;
  for(let i=0;i<n;i++){const v=offNum[i]/offDen[i];delta=Math.max(delta,Math.abs(v-off[i]));off[i]=v;}
  const defNum=new Array<number>(n).fill(0),defDen=new Array<number>(n).fill(cfg.ridge);
  for(const o of obs){defNum[o.dfn]+=o.w*(o.pts-mu-o.side-off[o.atk]);defDen[o.dfn]+=o.w;}
  for(let i=0;i<n;i++){const v=defNum[i]/defDen[i];delta=Math.max(delta,Math.abs(v-def[i]));def[i]=v;}
  if(delta<1e-6)break;
 }
 const offense=new Map(teams.map((t,i)=>[t,off[i]])),defense=new Map(teams.map((t,i)=>[t,def[i]]));
 return {mu,games:games.length,offense,defense,
  predict(home,away,neutral){
   const oh=offense.get(home),oa=offense.get(away),dh=defense.get(home),da=defense.get(away);
   if(oh===undefined||oa===undefined||dh===undefined||da===undefined)return null;
   const side=neutral?0:cfg.homeEdge/2;
   const h=mu+side+oh+da,a=mu-side+oa+dh;
   return {home:h,away:a,total:h+a};
  }};
}
/** Benchmark: recency-weighted league average total before `asOf`. */
export function leagueAverageTotal(history:CompletedGame[],sport:EngineSport,asOf:Date):number|null{
 const cfg=settings[sport],cutoff=asOf.getTime();
 let w=0,s=0;
 for(const g of history){
  const t=Date.parse(g.date);if(!(t<cutoff))continue;
  const weight=Math.pow(0.5,(cutoff-t)/DAY/cfg.halfLifeDays);
  w+=weight;s+=weight*(g.homeScore+g.awayScore);
 }
 return w>0?s/w:null;
}
