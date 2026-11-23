import type {MarketQuote} from "../contracts";

/** Normalize team names across providers (ESPN uses "LA Clippers", The Odds API "Los Angeles Clippers"). */
export function teamKey(name:string):string{
 return name.toLowerCase().replace(/^la\s/,"los angeles ").replace(/[^a-z0-9]+/g," ").trim();
}
const median=(xs:number[])=>{const s=[...xs].sort((a,b)=>a-b),m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2;};
/**
 * Consensus pregame line for one game from LIVE quotes only: median home spread and
 * median total across books. Simulated quotes never produce a market line.
 */
export function consensusLine(quotes:MarketQuote[],home:string,away:string):{spreadHome:number|null;total:number|null;books:number}{
 const h=teamKey(home),a=teamKey(away);
 const game=quotes.filter(q=>q.state==="live"&&teamKey(q.home)===h&&teamKey(q.away)===a);
 const spreads=game.filter(q=>q.market==="spread"&&teamKey(q.selection)===h&&Number.isFinite(q.line)).map(q=>q.line!);
 const totals=game.filter(q=>q.market==="total"&&/^over$/i.test(q.selection)&&Number.isFinite(q.line)).map(q=>q.line!);
 return {spreadHome:spreads.length?median(spreads):null,total:totals.length?median(totals):null,books:new Set(game.map(q=>q.book)).size};
}
