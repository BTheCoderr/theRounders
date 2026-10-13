export const SPORTS=["NBA","NFL","NHL","MLB"] as const;
export type Sport=typeof SPORTS[number];
export type MarketName="moneyline"|"spread"|"total";
export type DataState="live"|"simulated";
export type Quote={
 eventId:string;sport:string;market:MarketName;selection:string;line?:number;
 price:number;book:string;updatedAt:string;state:DataState;
 away:string;home:string;startTime:string;
};
export type Group={key:string;first:Quote;quotes:Quote[];best:Quote};
export const fmtPrice=(price:number)=>price>0?"+"+price:String(price);
export const impliedProbability=(price:number)=>price<0?100*(-price)/(100-price):10000/(price+100);
export function validQuote(q:unknown):q is Quote{
 if(!q||typeof q!=="object")return false;
 const v=q as Record<string,unknown>;
 return ["eventId","selection","book","away","home"].every(k=>typeof v[k]==="string"&&String(v[k]).length>0)
  &&["moneyline","spread","total"].includes(String(v.market))
  &&["live","simulated"].includes(String(v.state))
  &&typeof v.price==="number"&&Number.isFinite(v.price)&&Math.abs(v.price)>=100
  &&(v.line===undefined||typeof v.line==="number"&&Number.isFinite(v.line));
}
export function groupQuotes(quotes:Quote[],market:MarketName):Group[]{
 const grouped=new Map<string,Quote[]>();
 for(const q of quotes){
  if(!validQuote(q)||q.market!==market)continue;
  const key=JSON.stringify([q.eventId,q.market,q.selection,q.line??null,q.state]);
  grouped.set(key,[...(grouped.get(key)||[]),q]);
 }
 return [...grouped].map(([key,rows])=>{
  const sorted=[...rows].sort((a,b)=>b.price-a.price);
  return {key,quotes:sorted,first:sorted[0],best:sorted[0]};
 });
}
export type PriceGap={key:string;first:Quote;best:Quote;worst:Quote;gap:number};
export function getPriceGaps(quotes:Quote[]):PriceGap[]{
 const result:PriceGap[]=[];
 for(const market of ["moneyline","spread","total"] as const){
  for(const group of groupQuotes(quotes,market)){
   const books=new Map<string,Quote>();
   for(const q of group.quotes)if(!books.has(q.book))books.set(q.book,q);
   const options=[...books.values()].sort((a,b)=>b.price-a.price);
   if(options.length<2)continue;
   const best=options[0],worst=options[options.length-1];
   const gap=impliedProbability(worst.price)-impliedProbability(best.price);
   if(gap>=1.5)result.push({key:group.key,first:group.first,best,worst,gap});
  }
 }
 return result.sort((a,b)=>b.gap-a.gap);
}
export function demoQuotes(sport:Sport):Quote[]{
 const ts=new Date().toISOString();
 const events=[["Sample Away","Sample Home"],["Practice Blue","Practice Gold"]];
 return events.flatMap(([away,home],i)=>[["Sample Book A",-110],["Sample Book B",105]].flatMap(([book,price])=>
  (["moneyline","spread","total"] as MarketName[]).map(market=>({
   eventId:"demo-"+sport+"-"+i,sport,market,away,home,
   selection:market==="total"?"Over":home,
   line:market==="spread"?-3.5:market==="total"?220.5:undefined,
   price:Number(price),book:String(book),updatedAt:ts,state:"simulated" as const,
   startTime:ts,
  }))
 ));
}
