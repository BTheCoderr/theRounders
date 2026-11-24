/** Experimental challenger; not registered in the live engine. Fit only on settled, pre-cutoff forecasts. */
export type Forecast={eventId:string;startsAt:string;settledAt:string;actualMargin:number;margins:Record<string,number>};
export function fitWeights(rows:readonly Forecast[],members:readonly string[],cutoff:Date,minGames=100){
 if(!members.length||new Set(members).size!==members.length)throw new Error("Unique members required");
 const seen=new Set<string>();
 const train=rows.filter(r=>{
  const start=Date.parse(r.startsAt),end=Date.parse(r.settledAt);
  if(!(start<end&&end<cutoff.getTime())||seen.has(r.eventId)||!Number.isFinite(r.actualMargin)||!members.every(m=>Number.isFinite(r.margins[m])))return false;
  seen.add(r.eventId);return true;
 });
 const equal=Object.fromEntries(members.map(m=>[m,1/members.length]));
 if(train.length<minGames)return {weights:equal,games:train.length,trained:false};
 const errors=members.map(m=>train.reduce((s,r)=>s+Math.abs(r.margins[m]-r.actualMargin),0)/train.length);
 const inverse=errors.map(e=>1/Math.max(e,0.01)),sum=inverse.reduce((a,b)=>a+b,0);
 // Shrink toward equal weights to reduce overfitting.
 return {weights:Object.fromEntries(members.map((m,i)=>[m,0.5/members.length+0.5*inverse[i]/sum])),games:train.length,trained:true};
}
export function weightedMargin(margins:Record<string,number>,weights:Record<string,number>):number|null{
 const entries=Object.entries(weights);
 if(!entries.length||entries.some(([m,w])=>!Number.isFinite(margins[m])||!Number.isFinite(w)||w<0))return null;
 const sum=entries.reduce((s,[,w])=>s+w,0);
 return sum>0?entries.reduce((s,[m,w])=>s+margins[m]*w,0)/sum:null;
}
