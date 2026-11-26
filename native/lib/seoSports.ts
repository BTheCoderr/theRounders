import {SPORT_CONFIG,isSport,type Sport} from "./sports";
/** URL segment <-> sport, plus display names for page titles. */
export const SPORT_SLUGS=["nba","nfl","ncaam","ncaaf","nhl","mlb"] as const;
export function sportFromSlug(slug:string):Sport|null{const s=slug.toUpperCase();return isSport(s)?s:null;}
export const sportTitle=(s:Sport)=>SPORT_CONFIG[s].label;
export const seasonText=(s:Sport,y:number)=>s==="NFL"||s==="NCAAF"||s==="MLB"?String(y):`${y}–${String(y+1).slice(2)}`;
