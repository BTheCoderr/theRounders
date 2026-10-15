import type {TeamGame} from "./ratings";

/** A Massey-inspired, regularized margin model. This is NOT Kenneth Massey's proprietary ratings. */
export type Sport="NBA"|"NFL"|"NHL"|"MLB";
export type CompletedGame={
  date:string;home:string;away:string;homeScore:number;awayScore:number;neutral:boolean;
};
export type PowerRank={
  rank:number;team:string;rating:number;games:number;record:{wins:number;losses:number;ties:number};
  averageOpponentRating:number;adjustedMargin:number;recentForm:number;
};
export type PowerBoard={
  model:"rounders-power-v2-preview";sport:Sport;asOf:string;method:string;games:number;
  parameters:{ridge:number;halfLifeDays:number;marginCap:number;homeAdvantage:number};
  rankings:PowerRank[];
};
const parameters:Record<Sport,{ridge:number;halfLifeDays:number;marginCap:number;homeAdvantage:number}>={
  NBA:{ridge:1.25,halfLifeDays:45,marginCap:25,homeAdvantage:2.2},
  NFL:{ridge:1.25,halfLifeDays:60,marginCap:17,homeAdvantage:2.2},
  NHL:{ridge:1.25,halfLifeDays:50,marginCap:3,homeAdvantage:0.18},
  MLB:{ridge:1.25,halfLifeDays:35,marginCap:5,homeAdvantage:0.25}
};
const round=(n:number,d=2)=>Number(n.toFixed(d));
const average=(nums:number[])=>nums.length?nums.reduce((a,b)=>a+b,0)/nums.length:0;
const dot=(a:number[],b:number[])=>a.reduce((v,x,i)=>v+x*b[i],0);
const day=86400000;

/** Deduplicate mirrored ESPN-style rows, reject invalid/future records and keep a single home-oriented game. */
export function uniqueCompletedGames(rows:TeamGame[],asOf=new Date()):CompletedGame[]{
  const seen=new Set<string>();
  const out:CompletedGame[]=[];
  const now=asOf.getTime();
  if(!Number.isFinite(now))return [];
  for(const r of rows){
    if(!r||!["home","away","neutral"].includes(r.location)||
      !r.team?.trim()||!r.opponent?.trim()||r.team===r.opponent||
      !Number.isFinite(r.teamScore)||!Number.isFinite(r.opponentScore)||
      r.teamScore<0||r.opponentScore<0)continue;
    const timestamp=Date.parse(r.date);
    if(!Number.isFinite(timestamp)||timestamp>now)continue;
    const neutral=r.location==="neutral";
    const home=neutral?(r.team<r.opponent?r.team:r.opponent):r.location==="home"?r.team:r.opponent;
    const away=neutral?(r.team<r.opponent?r.opponent:r.team):r.location==="home"?r.opponent:r.team;
    const homeScore=home===r.team?r.teamScore:r.opponentScore;
    const awayScore=home===r.team?r.opponentScore:r.teamScore;
    const key=JSON.stringify([timestamp,home,away,homeScore,awayScore,neutral]);
    if(seen.has(key))continue;
    seen.add(key);
    out.push({date:new Date(timestamp).toISOString(),home,away,homeScore,awayScore,neutral});
  }
  return out.sort((a,b)=>Date.parse(a.date)-Date.parse(b.date)||a.home.localeCompare(b.home));
}
/**
 * Solve (XᵀWX + λI)r = XᵀWy via conjugate gradient.
 * λ>0 makes the sparse schedule graph solvable even when disconnected.
 * We use recency weights and bounded score margins, not fabricated certainty.
 */
export function computePowerBoard(rows:TeamGame[],sport:Sport,asOf=new Date()):PowerBoard{
  const config=parameters[sport];
  if(!config)throw new Error("Unsupported sport");
  const games=uniqueCompletedGames(rows,asOf);
  const teams=[...new Set(games.flatMap(g=>[g.home,g.away]))].sort();
  const index=new Map(teams.map((t,i)=>[t,i]));
  const n=teams.length;
  const diag=new Array<number>(n).fill(config.ridge);
  const rhs=new Array<number>(n).fill(0);
  type Edge={h:number;a:number;w:number;target:number};
  const edges:Edge[]=[];
  for(const game of games){
    const h=index.get(game.home)!,a=index.get(game.away)!;
    const age=Math.max(0,(asOf.getTime()-Date.parse(game.date))/day);
    const w=Math.pow(0.5,age/config.halfLifeDays);
    const margin=Math.max(-config.marginCap,Math.min(config.marginCap,game.homeScore-game.awayScore));
    const target=margin-(game.neutral?0:config.homeAdvantage);
    diag[h]+=w;diag[a]+=w;rhs[h]+=w*target;rhs[a]-=w*target;
    edges.push({h,a,w,target});
  }
  const mul=(v:number[])=>{
    const out=diag.map((d,i)=>d*v[i]);
    for(const e of edges){out[e.h]-=e.w*v[e.a];out[e.a]-=e.w*v[e.h]}
    return out;
  };
  const x=new Array<number>(n).fill(0);
  let residue=[...rhs];
  let z=residue.map((v,i)=>v/diag[i]);
  let p=[...z];
  let rs=dot(residue,z);
  for(let i=0;i<Math.min(500,Math.max(30,n*8))&&rs>1e-18;i++){
    const ap=mul(p);
    const den=dot(p,ap);
    if(!(den>0))break;
    const alpha=rs/den;
    for(let j=0;j<n;j++){x[j]+=alpha*p[j];residue[j]-=alpha*ap[j]}
    z=residue.map((v,j)=>v/diag[j]);
    const next=dot(residue,z);
    if(next<1e-18)break;
    const beta=next/rs;
    p=p.map((v,j)=>z[j]+beta*v);
    rs=next;
  }
  const center=average(x);
  const rank=teams.map((team,i)=>{
    const own=games.filter(g=>g.home===team||g.away===team);
    const margins=own.map(g=>(g.home===team?g.homeScore-g.awayScore:g.awayScore-g.homeScore));
    const opponents=own.map(g=>x[index.get(g.home===team?g.away:g.home)!]-center);
    const latest=own.slice(-5);
    const recent=latest.map(g=>g.home===team?g.homeScore-g.awayScore:g.awayScore-g.homeScore);
    return {
      rank:0,team,rating:round(x[i]-center),games:own.length,
      record:{wins:margins.filter(v=>v>0).length,losses:margins.filter(v=>v<0).length,ties:margins.filter(v=>v===0).length},
      averageOpponentRating:round(average(opponents)),
      adjustedMargin:round(average(margins)),
      recentForm:round(average(recent))
    };
  }).sort((a,b)=>b.rating-a.rating||a.team.localeCompare(b.team));
  rank.forEach((r,i)=>{r.rank=i+1});
  return {model:"rounders-power-v2-preview",sport,asOf:asOf.toISOString(),
    method:"Recency-weighted regularized least-squares point margin, capped for diminishing returns; strength-of-schedule is jointly adjusted.",
    games:games.length,parameters:{...config},rankings:rank};
}

export type HoldoutResult={method:"chronological-70-30";evaluatedGames:number;skippedUnknownTeams:number;
  modelMAE:number|null;homeBaselineMAE:number|null;beatsBaseline:boolean|null;warning:string};
/** Strict past-only train and future-only evaluation, not an accuracy claim or calibrated betting model. */
export function holdoutMarginEvaluation(rows:TeamGame[],sport:Sport,asOf=new Date()):HoldoutResult{
  const games=uniqueCompletedGames(rows,asOf);
  const split=Math.floor(games.length*0.7);
  const empty={method:"chronological-70-30" as const,evaluatedGames:0,skippedUnknownTeams:0,
    modelMAE:null,homeBaselineMAE:null,beatsBaseline:null as boolean|null,
    warning:"Not enough eligible historical games to evaluate out-of-sample performance."};
  if(split<10||games.length-split<5)return empty;
  const train=games.slice(0,split);
  const test=games.slice(split);
  const rowsForTrain:TeamGame[]=train.map(g=>({
    date:g.date,team:g.home,opponent:g.away,teamScore:g.homeScore,opponentScore:g.awayScore,location:g.neutral?"neutral" as const:"home" as const
  }));
  const board=computePowerBoard(rowsForTrain,sport,new Date(train[train.length-1].date));
  const ratings=new Map(board.rankings.map(r=>[r.team,r.rating]));
  let modelError=0,baselineError=0,count=0,skipped=0;
  for(const g of test){
    const h=ratings.get(g.home),a=ratings.get(g.away);
    if(h===undefined||a===undefined){skipped++;continue}
    const hfa=g.neutral?0:board.parameters.homeAdvantage;
    const margin=g.homeScore-g.awayScore;
    modelError+=Math.abs(margin-(h-a+hfa));
    baselineError+=Math.abs(margin-hfa);
    count++;
  }
  if(count<5)return {...empty,skippedUnknownTeams:skipped};
  const modelMAE=round(modelError/count),homeBaselineMAE=round(baselineError/count);
  return {method:"chronological-70-30",evaluatedGames:count,skippedUnknownTeams:skipped,
    modelMAE,homeBaselineMAE,beatsBaseline:modelMAE<homeBaselineMAE,
    warning:"Preliminary one-split historical holdout, not a published/independently validated accuracy estimate. Parameters are unoptimized."};
}
