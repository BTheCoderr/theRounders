export const SPORTS=["NBA","NFL","NHL","MLB"] as const;
export type Sport=typeof SPORTS[number];
/** Abbreviations from the deployed demo feed, mapped to ESPN display names the ratings model uses. */
const TEAM_NAMES:Record<Sport,Record<string,string>>={
 NBA:{BOS:"Boston Celtics",NYK:"New York Knicks",LAL:"Los Angeles Lakers",GSW:"Golden State Warriors",MIL:"Milwaukee Bucks",CLE:"Cleveland Cavaliers"},
 NFL:{BUF:"Buffalo Bills",NYJ:"New York Jets",DAL:"Dallas Cowboys",PHI:"Philadelphia Eagles",KC:"Kansas City Chiefs",DEN:"Denver Broncos"},
 NHL:{BOS:"Boston Bruins",NYR:"New York Rangers",TOR:"Toronto Maple Leafs",MTL:"Montreal Canadiens",VGK:"Vegas Golden Knights",EDM:"Edmonton Oilers"},
 MLB:{BOS:"Boston Red Sox",NYY:"New York Yankees",LAD:"Los Angeles Dodgers",SD:"San Diego Padres",CHC:"Chicago Cubs",STL:"St. Louis Cardinals"},
};
export function displayTeam(sport:string,name:string){return TEAM_NAMES[sport as Sport]?.[name]??name;}
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
const DEMO_BOARD:Record<Sport,{games:[string,string][];spread:number;total:number}>={
 NBA:{games:[["Boston Celtics","New York Knicks"],["Los Angeles Lakers","Golden State Warriors"]],spread:-3.5,total:220.5},
 NFL:{games:[["Buffalo Bills","New York Jets"],["Dallas Cowboys","Philadelphia Eagles"]],spread:-3.5,total:45.5},
 NHL:{games:[["Boston Bruins","New York Rangers"],["Toronto Maple Leafs","Montreal Canadiens"]],spread:-1.5,total:6.5},
 MLB:{games:[["Boston Red Sox","New York Yankees"],["Los Angeles Dodgers","San Diego Padres"]],spread:-1.5,total:8.5},
};
export function demoQuotes(sport:Sport):Quote[]{
 const ts=new Date().toISOString();
 const board=DEMO_BOARD[sport];
 return board.games.flatMap(([away,home],i)=>[["Sample Book A",-110],["Sample Book B",105]].flatMap(([book,price])=>
  (["moneyline","spread","total"] as MarketName[]).map(market=>({
   eventId:"demo-"+sport+"-"+i,sport,market,away,home,
   selection:market==="total"?"Over":home,
   line:market==="spread"?board.spread:market==="total"?board.total:undefined,
   price:Number(price),book:String(book),updatedAt:ts,state:"simulated" as const,
   startTime:ts,
  }))
 ));
}
