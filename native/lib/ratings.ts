import type {MarketName} from "./contracts";

export type TeamGame={
  date:string;team:string;opponent:string;teamScore:number;opponentScore:number;
  location:"home"|"away"|"neutral";
};

export type TeamRating={
  team:string;power:number;offense:number;defense:number;sos:number;
  games:number;uncertainty:number;
};

export type MatchupProjection={
  away:string;home:string;awayRating:TeamRating;homeRating:TeamRating;
  projectedAway:number;projectedHome:number;fairSpreadHome:number;
  homeWinProbability:number;confidence:number;state:"model";
  factors:{power:number;homeAdvantage:number;uncertainty:number};
};

const mean=(xs:number[])=>xs.length?xs.reduce((a,b)=>a+b,0)/xs.length:0;
const logistic=(x:number)=>1/(1+Math.exp(-x));
const clamp=(n:number,a:number,b:number)=>Math.max(a,Math.min(b,n));

/**
 * Opponent-adjusted Rounders rating model.
 * Positive power means stronger than league average. Offense/defense are
 * points above/below league scoring baseline. No sportsbook data is used
 * here, keeping the model independent from the market.
 */
export function buildRatings(games:TeamGame[],iterations=24):Map<string,TeamRating>{
  const teams=[...new Set(games.flatMap(g=>[g.team,g.opponent]))];
  const leaguePoints=mean(games.map(g=>g.teamScore));
  const byTeam=new Map(teams.map(t=>[t,games.filter(g=>g.team===t)]));
  let power=new Map(teams.map(t=>[t,0]));
  for(let i=0;i<iterations;i++){
    const next=new Map<string,number>();
    for(const team of teams){
      const rows=byTeam.get(team)||[];
      next.set(team,mean(rows.map(g=>(g.teamScore-g.opponentScore)+(power.get(g.opponent)||0))));
    }
    const center=mean([...next.values()]);
    power=new Map([...next].map(([t,v])=>[t,v-center]));
  }
  const out=new Map<string,TeamRating>();
  for(const team of teams){
    const rows=byTeam.get(team)||[];
    const opp=rows.map(g=>power.get(g.opponent)||0);
    const offense=mean(rows.map(g=>g.teamScore-leaguePoints));
    const defense=mean(rows.map(g=>leaguePoints-g.opponentScore));
    const margins=rows.map(g=>g.teamScore-g.opponentScore);
    const avg=mean(margins);
    const variance=mean(margins.map(x=>(x-avg)**2));
    out.set(team,{team,power:power.get(team)||0,offense,defense,sos:mean(opp),games:rows.length,uncertainty:Math.sqrt(variance/Math.max(1,rows.length))});
  }
  return out;
}

export function projectMatchup(ratings:Map<string,TeamRating>,away:string,home:string,leagueBaseline=112,homeAdvantage=2.2):MatchupProjection|null{
  const a=ratings.get(away),h=ratings.get(home); if(!a||!h)return null;
  const projectedAway=leagueBaseline+a.offense-h.defense;
  const projectedHome=leagueBaseline+h.offense-a.defense+homeAdvantage;
  const fairSpreadHome=-(projectedHome-projectedAway);
  const ratingDiff=(h.power-a.power)+homeAdvantage;
  const uncertainty=Math.sqrt(a.uncertainty**2+h.uncertainty**2);
  const homeWinProbability=logistic(ratingDiff/6.5)*100;
  const sample=Math.min(a.games,h.games);
  const confidence=clamp(45+sample*2.2-uncertainty*1.4,35,92);
  return{away,home,awayRating:a,homeRating:h,projectedAway,projectedHome,fairSpreadHome,homeWinProbability,confidence,state:"model",factors:{power:h.power-a.power,homeAdvantage,uncertainty}};
}

export function marketEdge(modelProbability:number,americanOdds:number){
  const implied=americanOdds<0?(-americanOdds)/((-americanOdds)+100)*100:100/(americanOdds+100)*100;
  return{implied,edge:modelProbability-implied};
}

export function fairAmerican(probability:number){
  const p=clamp(probability,0.01,99.99)/100;
  return p>=.5?-Math.round((p/(1-p))*100):Math.round(((1-p)/p)*100);
}

export function modelProbabilityForSelection(p:MatchupProjection,selection:string,market:MarketName){
  if(market!=="moneyline")return null;
  if(selection===p.home)return p.homeWinProbability;
  if(selection===p.away)return 100-p.homeWinProbability;
  return null;
}
