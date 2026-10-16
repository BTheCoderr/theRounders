import type {TeamGame} from "./ratings";
import {uniqueCompletedGames,type Sport,type CompletedGame} from "./powerRatings";

export type ResearchOptions={
 halfLifeDays:number;
 ridge:number;
 huberDelta:number;
 homeRidge:number;
 priorHomeAdvantage:number;
 priorRetention:number;
 /** Only predictions or ratings from an earlier season are valid priors. */
 priorRatings?:ReadonlyMap<string,number>;
};
export type ResearchFit={
 model:"rounders-research-v2.1";sport:Sport;cutoff:string;games:number;
 homeAdvantage:number;ratings:Map<string,number>;
 options:Omit<ResearchOptions,"priorRatings">;
 warning:string;
};
const defaults:Record<Sport,Omit<ResearchOptions,"priorRatings">>={
 NBA:{halfLifeDays:45,ridge:1.25,huberDelta:12,homeRidge:20,priorHomeAdvantage:2.2,priorRetention:0},
 NFL:{halfLifeDays:60,ridge:1.25,huberDelta:9,homeRidge:20,priorHomeAdvantage:2.2,priorRetention:0},
 NHL:{halfLifeDays:50,ridge:1.25,huberDelta:1.5,homeRidge:20,priorHomeAdvantage:0.18,priorRetention:0},
 MLB:{halfLifeDays:35,ridge:1.25,huberDelta:2.5,homeRidge:20,priorHomeAdvantage:0.25,priorRetention:0}
};
const msDay=86400000;
const dot=(a:number[],b:number[])=>a.reduce((s,v,i)=>s+v*b[i],0);
const clamp=(n:number,a:number,b:number)=>Math.max(a,Math.min(b,n));
function solveRatings(n:number,edges:Array<{home:number;away:number;weight:number;target:number}>,ridge:number,prior:number[]){
 const diagonal=Array(n).fill(ridge) as number[];
 const rhs=prior.map(v=>ridge*v);
 for(const e of edges){diagonal[e.home]+=e.weight;diagonal[e.away]+=e.weight;
  rhs[e.home]+=e.weight*e.target;rhs[e.away]-=e.weight*e.target;}
 const multiply=(x:number[])=>{
  const out=diagonal.map((v,i)=>v*x[i]);
  for(const e of edges){out[e.home]-=e.weight*x[e.away];out[e.away]-=e.weight*x[e.home];}
  return out;
 };
 let x=prior.slice();
 let r=rhs.map((v,i)=>v-multiply(x)[i]);
 let z=r.map((v,i)=>v/diagonal[i]);
 let p=z.slice(),rz=dot(r,z);
 for(let k=0;k<Math.max(32,Math.min(350,n*8))&&rz>1e-16;k++){
  const ap=multiply(p),den=dot(p,ap);if(!(den>0))break;
  const alpha=rz/den;
  x=x.map((v,i)=>v+alpha*p[i]);
  r=r.map((v,i)=>v-alpha*ap[i]);
  z=r.map((v,i)=>v/diagonal[i]);
  const next=dot(r,z);if(next<1e-16)break;
  const beta=next/rz;p=z.map((v,i)=>v+beta*p[i]);rz=next;
 }
 return x;
}

/** Experimental, Huber-reweighted least squares. Fit at cutoff only, never on same-day/future results. */
export function fitResearchRpi(rows:TeamGame[],sport:Sport,cutoff:Date,overrides:Partial<ResearchOptions>={}):ResearchFit{
 if(!defaults[sport])throw new Error("Unsupported sport");
 if(!Number.isFinite(cutoff.getTime()))throw new Error("Invalid training cutoff");
 const opts={...defaults[sport],...overrides};
 if(!Number.isFinite(opts.halfLifeDays)||opts.halfLifeDays<=0||
    !Number.isFinite(opts.ridge)||opts.ridge<=0||
    !Number.isFinite(opts.huberDelta)||opts.huberDelta<=0||
    !Number.isFinite(opts.homeRidge)||opts.homeRidge<=0||
    !Number.isFinite(opts.priorHomeAdvantage)||
    !Number.isFinite(opts.priorRetention)||opts.priorRetention<0||opts.priorRetention>1)
    throw new Error("Invalid research model parameters");
 // A game starting at cutoff is never considered known. Completed final results only.
 const games=uniqueCompletedGames(rows,new Date(cutoff.getTime()-1));
 const teams=[...new Set(games.flatMap(g=>[g.home,g.away]))].sort();
 const ids=new Map(teams.map((team,i)=>[team,i]));
 const priors=teams.map(t=>{
  const v=opts.priorRatings?.get(t);
  return Number.isFinite(v)?v!*opts.priorRetention:0;
 });
 type Edge={h:number;a:number;margin:number;neutral:boolean;weight:number;effective:number};
 const edges:Edge[]=games.map(g=>({
  h:ids.get(g.home)!,a:ids.get(g.away)!,margin:g.homeScore-g.awayScore,neutral:g.neutral,
  weight:Math.pow(0.5,(cutoff.getTime()-Date.parse(g.date))/msDay/opts.halfLifeDays),effective:0
 }));
 let rating=priors.slice(),home=opts.priorHomeAdvantage;
 for(let k=0;k<12;k++){
  const fitting:Array<{home:number;away:number;weight:number;target:number}>=[];
  for(const e of edges){
   const error=e.margin-(rating[e.h]-rating[e.a]+(e.neutral?0:home));
   const robust=Math.abs(error)<=opts.huberDelta?1:opts.huberDelta/Math.abs(error);
   e.effective=e.weight*robust;
   fitting.push({home:e.h,away:e.a,weight:e.effective,target:e.margin-(e.neutral?0:home)});
  }
  const next=solveRatings(teams.length,fitting,opts.ridge,priors);
  const numerator=opts.homeRidge*opts.priorHomeAdvantage;
  let totalNumerator=numerator,denominator=opts.homeRidge;
  for(const e of edges){if(!e.neutral){
    totalNumerator+=e.effective*(e.margin-next[e.h]+next[e.a]);
    denominator+=e.effective;
  }}
  const updatedHome=clamp(totalNumerator/denominator,-25,25);
  const difference=Math.max(Math.abs(updatedHome-home),...next.map((v,i)=>Math.abs(v-rating[i])));
  rating=next;home=updatedHome;
  if(difference<1e-5)break;
 }
 // Center the league mean to zero; rating differences remain unchanged.
 const center=rating.length?rating.reduce((s,v)=>s+v,0)/rating.length:0;
 return {
  model:"rounders-research-v2.1",sport,cutoff:cutoff.toISOString(),games:games.length,
  homeAdvantage:Number(home.toFixed(4)),
  ratings:new Map(teams.map((t,i)=>[t,Number((rating[i]-center).toFixed(5))])),
  options:{
   halfLifeDays:opts.halfLifeDays,ridge:opts.ridge,huberDelta:opts.huberDelta,
   homeRidge:opts.homeRidge,priorHomeAdvantage:opts.priorHomeAdvantage,
   priorRetention:opts.priorRetention
  },
  warning:"Experimental fixed parameters. No calibrated win probabilities or claimed improvement; requires locked cross-season validation."
 };
}
