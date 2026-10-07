import type {TeamGame} from "./ratings";

/**
 * Controlled model-training sample. This is deliberately labeled simulated.
 * Replace through the same contract with an authorized historical-results
 * provider without changing the rating mathematics or UI.
 */
const strengths:Record<string,Record<string,number>>={
 NBA:{BOS:8,NYK:5,LAL:2,GSW:4,MIL:6,CLE:7},
 NFL:{BUF:7,NYJ:-2,DAL:3,PHI:7,KC:8,DEN:4},
 NHL:{BOS:6,NYR:5,TOR:4,MTL:-2,VGK:5,EDM:7},
 MLB:{BOS:3,NYY:6,LAD:8,SD:5,CHC:2,STL:1}
};
export function demoHistory(sport:string):TeamGame[]{
 const table=strengths[sport]||strengths.NBA,teams=Object.keys(table),games:TeamGame[]=[];
 for(let round=0;round<10;round++) for(let i=0;i<teams.length;i++){
   const team=teams[i],opponent=teams[(i+round% (teams.length-1)+1)%teams.length];
   const home=round%2===0;
   const noise=((team.charCodeAt(0)+opponent.charCodeAt(1)+round*7)%9)-4;
   const baseline=sport==="NFL"?23:sport==="NHL"?3:sport==="MLB"?4.5:112;
   const scale=sport==="NHL"?.18:sport==="MLB"?.35:1;
   const margin=(table[team]-table[opponent])*scale+(home?1.5:-1.5)+noise*scale;
   games.push({date:new Date(Date.now()-(round+1)*86400000).toISOString(),team,opponent,teamScore:baseline+margin/2,opponentScore:baseline-margin/2,location:home?"home":"away"});
 }
 return games;
}
