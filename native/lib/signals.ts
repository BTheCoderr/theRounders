import type {MarketQuote,MarketName} from "./contracts";
export type LineShopGap={key:string;eventId:string;sport:string;matchup:string;market:MarketName;selection:string;line?:number;bestBook:string;bestPrice:number;worstBook:string;worstPrice:number;impliedGapPoints:number;state:"live"|"simulated"};
const implied=(price:number)=>price<0?100*(-price)/(100-price):10000/(price+100);
/** Compare independently quoted prices for the SAME market/selection/line.
 * An odds snapshot cannot prove STEAM or reverse line movement.
 */
export function findLineShopGaps(quotes:MarketQuote[],threshold=1.5):LineShopGap[]{
 const groups=new Map<string,MarketQuote[]>();
 for(const q of quotes){
  if(!q||!["moneyline","spread","total"].includes(q.market)||!Number.isFinite(q.price)||q.price===0||Math.abs(q.price)<100||q.line!==undefined&&!Number.isFinite(q.line)||!q.book||!q.selection||!q.eventId||!["live","simulated"].includes(q.state))continue;
  const key=JSON.stringify([q.eventId,q.market,q.selection,q.line??null,q.state]);
  groups.set(key,[...(groups.get(key)||[]),q]);
 }
 const gaps:LineShopGap[]=[];
 for(const [key,entries] of groups){
  const byBook=new Map<string,MarketQuote>();
  for(const q of entries){const old=byBook.get(q.book);if(!old||q.price>old.price)byBook.set(q.book,q)}
  const options=[...byBook.values()].sort((a,b)=>b.price-a.price);
  if(options.length<2)continue;
  const [best]=options,worst=options[options.length-1],gap=implied(worst.price)-implied(best.price);
  if(gap<threshold)continue;
  gaps.push({key,eventId:best.eventId,sport:best.sport,matchup:best.away+" @ "+best.home,market:best.market,selection:best.selection,line:best.line,bestBook:best.book,bestPrice:best.price,worstBook:worst.book,worstPrice:worst.price,impliedGapPoints:Number(gap.toFixed(2)),state:best.state});
 }
 return gaps.sort((a,b)=>b.impliedGapPoints-a.impliedGapPoints);
}
