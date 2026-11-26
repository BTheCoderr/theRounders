import type {Sport} from "../sports.ts";

/**
 * Pregame betting lines that ESPN's public scoreboard carries (usually one sportsbook,
 * e.g. DraftKings). ESPN's API is unofficial and unlicensed, so these lines are used
 * ONLY internally (closing-line value, market Brier); they are never shown in the line shop.
 *
 * Parsing is defensive: the sign of the home spread must be confirmed by the favorite
 * flags or the "ABBR -x" details string; otherwise the spread is left null, never guessed.
 */
type TeamOdds={favorite?:boolean;underdog?:boolean;moneyLine?:number|string};
type LinePair={open?:{line?:string|number;odds?:string|number};close?:{line?:string|number;odds?:string|number}};
export type EspnOdds={
 provider?:{id?:string;name?:string};details?:string;overUnder?:number|string;spread?:number|string;
 homeTeamOdds?:TeamOdds;awayTeamOdds?:TeamOdds;
 pointSpread?:{home?:LinePair;away?:LinePair};total?:{over?:LinePair;under?:LinePair};
 moneyline?:{home?:LinePair;away?:LinePair};
};
type Competitor={homeAway?:string;team?:{id?:string;displayName?:string;abbreviation?:string}};
export type EspnEvent={id?:string;date?:string;season?:{type?:number|string};status?:{type?:{state?:string}};
 competitions?:Array<{competitors?:Competitor[];odds?:EspnOdds[]}>};

export type EspnLine={eventId:string;startsAt:string;home:string;away:string;homeId:string;awayId:string;book:string;
 spreadHome:number|null;total:number|null;homeMoneyline:number|null;awayMoneyline:number|null;homeWinProb:number|null;
 open:{spreadHome:number|null;total:number|null};raw:EspnOdds};

/** Largest believable |home spread| per sport; anything outside is treated as bad data. */
const SPREAD_CAP:Record<Sport,number>={NBA:35,NFL:35,NCAAM:50,NCAAF:65,NHL:4,MLB:4};
const TOTALS:Record<Sport,[number,number]>={NBA:[170,280],NFL:[25,70],NCAAM:[100,190],NCAAF:[25,90],NHL:[3.5,9],MLB:[5,15]};

/** "-5.5" | "+3" | "o220.5" | "u44" | "EVEN" | "PK" -> number; anything else -> null. */
export function lineNumber(v:unknown):number|null{
 if(typeof v==="number")return Number.isFinite(v)?v:null;
 if(typeof v!=="string")return null;
 const s=v.trim().toLowerCase();
 if(s==="pk"||s==="pick"||s==="even"||s==="ev")return 0;
 const m=/^[ou]?\s*([+-]?\d+(?:\.\d+)?)$/.exec(s);
 return m?Number(m[1]):null;
}
/** American moneyline: "EVEN" -> +100; zero or |x|<100 is invalid. */
export function moneyline(v:unknown):number|null{
 if(typeof v==="string"&&/^even$/i.test(v.trim()))return 100;
 const n=lineNumber(v);
 return n!==null&&Math.abs(n)>=100?n:null;
}
const implied=(p:number)=>p>0?100/(p+100):-p/(-p+100);

/** Home spread with a confirmed sign. */
function homeSpread(o:EspnOdds,homeAbbr:string,awayAbbr:string,which:"close"|"open",sport:Sport):number|null{
 const fromPair=lineNumber(o.pointSpread?.home?.[which]?.line);
 const fromAwayPair=lineNumber(o.pointSpread?.away?.[which]?.line);
 if(fromPair!==null&&fromAwayPair!==null&&Math.abs(fromPair+fromAwayPair)>0.01)return null;   // inconsistent book data
 let mag:number|null=fromPair!==null?Math.abs(fromPair):fromAwayPair!==null?Math.abs(fromAwayPair):null;
 if(which==="close"&&mag===null){const s=lineNumber(o.spread);if(s!==null)mag=Math.abs(s);}
 if(which==="close"&&mag===null){const d=/([+-]?\d+(?:\.\d+)?)\s*$/.exec(o.details||"");if(d)mag=Math.abs(Number(d[1]));}
 if(mag===null||mag>SPREAD_CAP[sport])return null;
 if(mag===0)return 0;
 // Sign sources, strongest first. Each must agree with any other that is present.
 const votes:number[]=[];
 if(fromPair!==null&&fromPair!==0)votes.push(Math.sign(fromPair));
 else if(fromAwayPair!==null&&fromAwayPair!==0)votes.push(-Math.sign(fromAwayPair));
 if(which==="close"){
  const homeFav=o.homeTeamOdds?.favorite===true||o.awayTeamOdds?.underdog===true;
  const awayFav=o.awayTeamOdds?.favorite===true||o.homeTeamOdds?.underdog===true;
  if(homeFav!==awayFav)votes.push(homeFav?-1:1);
  const d=/^\s*([A-Za-z0-9&.'-]+)\s+-\d/.exec(o.details||"");
  if(d){const ab=d[1].toUpperCase();if(ab===homeAbbr.toUpperCase())votes.push(-1);else if(ab===awayAbbr.toUpperCase())votes.push(1);}
 }
 if(!votes.length||votes.some(v=>v!==votes[0]))return null;
 return votes[0]*mag;
}

/** One line per scheduled event that has usable odds. */
export function parseEspnLines(events:readonly EspnEvent[],sport:Sport):EspnLine[]{
 const out:EspnLine[]=[];
 for(const e of events){
  if(e?.status?.type?.state!=="pre")continue;
  const c=e.competitions?.[0];const o=c?.odds?.[0];
  const start=Date.parse(e.date||"");const id=String(e.id||"").trim();
  if(!o||!id||!Number.isFinite(start))continue;
  const home=c?.competitors?.find(x=>x.homeAway==="home"),away=c?.competitors?.find(x=>x.homeAway==="away");
  if(!home?.team?.id||!away?.team?.id)continue;
  const ha=home.team.abbreviation||"",aa=away.team.abbreviation||"";
  const spreadHome=homeSpread(o,ha,aa,"close",sport);
  const [lo,hi]=TOTALS[sport];
  const tot=(v:unknown)=>{const t=lineNumber(v);return t!==null&&t>=lo&&t<=hi?t:null;};
  const total=tot(o.total?.over?.close?.line)??tot(o.overUnder);
  const hml=moneyline(o.moneyline?.home?.close?.odds)??moneyline(o.homeTeamOdds?.moneyLine);
  const aml=moneyline(o.moneyline?.away?.close?.odds)??moneyline(o.awayTeamOdds?.moneyLine);
  let prob:number|null=null;
  if(hml!==null&&aml!==null){const ih=implied(hml),ia=implied(aml);if(ih+ia>0.9&&ih+ia<1.25)prob=Number(Math.min(0.995,Math.max(0.005,ih/(ih+ia))).toFixed(4));}
  if(spreadHome===null&&total===null&&prob===null)continue;
  out.push({eventId:id,startsAt:new Date(start).toISOString(),home:home.team.displayName||"",away:away.team.displayName||"",
   homeId:String(home.team.id),awayId:String(away.team.id),book:o.provider?.name||"ESPN",
   spreadHome,total,homeMoneyline:hml,awayMoneyline:aml,homeWinProb:prob,
   open:{spreadHome:homeSpread(o,ha,aa,"open",sport),total:tot(o.total?.over?.open?.line)},raw:o});
 }
 return out;
}
