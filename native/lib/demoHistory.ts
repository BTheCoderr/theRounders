import type {TeamGame} from "./ratings";

/**
 * Controlled model-training sample. This is deliberately labeled simulated.
 * Replace through the same contract with an authorized historical-results
 * provider without changing the rating mathematics or UI.
 */
const strengths:Record<string,Record<string,number>>={
 NBA:{"Boston Celtics":8,"New York Knicks":5,"Los Angeles Lakers":2,"Golden State Warriors":4,"Milwaukee Bucks":6,"Cleveland Cavaliers":7},
 NFL:{"Buffalo Bills":7,"New York Jets":-2,"Dallas Cowboys":3,"Philadelphia Eagles":7,"Kansas City Chiefs":8,"Denver Broncos":4},
 NHL:{"Boston Bruins":6,"New York Rangers":5,"Toronto Maple Leafs":4,"Montreal Canadiens":-2,"Vegas Golden Knights":5,"Edmonton Oilers":7},
 MLB:{"Boston Red Sox":3,"New York Yankees":6,"Los Angeles Dodgers":8,"San Diego Padres":5,"Chicago Cubs":2,"St. Louis Cardinals":1}
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
