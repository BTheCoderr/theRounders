import {createHash} from "node:crypto";

/**
 * BALLDONTLIE (balldontlie.io). Player injuries need ALL-STAR ($9.99/mo per league) or
 * higher; NBA box scores (minutes, plus-minus) need GOAT ($39.99/mo per league).
 * Terms allow commercial display; building a substitute data feed is not allowed.
 * Injury reports are current-only: history exists here only from the day we start logging.
 */
export const BDL_BASE="https://api.balldontlie.io";
export const injuriesPath=(sport:"NBA"|"NFL")=>sport==="NBA"?"/v1/player_injuries":"/nfl/v1/player_injuries";

type Player={id:number|string;first_name?:string;last_name?:string;position?:string;position_abbreviation?:string;team_id?:number;team?:{id?:number;full_name?:string;name?:string}};
export type RawInjury={player?:Player;status?:string;description?:string;comment?:string;return_date?:string;date?:string};
export type Injury={playerId:string;name:string;teamId:string|null;team:string|null;position:string|null;
 status:string;description:string|null;returnDate:string|null;reportedAt:string|null;hash:string};

/** Normalize NBA and NFL injury rows. Rows without a player id or status are dropped, not guessed. */
export function parseInjuries(rows:RawInjury[],teamNames:ReadonlyMap<string,string>=new Map()):Injury[]{
 const out:Injury[]=[];
 for(const r of rows){
  const p=r.player;const status=(r.status||"").trim();
  if(!p||p.id===undefined||p.id===null||!status)continue;
  const teamId=p.team?.id!==undefined?String(p.team.id):p.team_id!==undefined?String(p.team_id):null;
  const team=p.team?.full_name||(teamId?teamNames.get(teamId)??null:null);
  const description=(r.description??r.comment??"").trim()||null;
  const returnDate=(r.return_date||"").trim()||null;
  const reportedAt=r.date&&Number.isFinite(Date.parse(r.date))?new Date(r.date).toISOString():null;
  const name=[p.first_name,p.last_name].filter(Boolean).join(" ").trim()||String(p.id);
  out.push({playerId:String(p.id),name,teamId,team,position:p.position_abbreviation||p.position||null,status,description,returnDate,reportedAt,
   hash:createHash("sha256").update([status,description??"",returnDate??"",teamId??""].join("|")).digest("hex").slice(0,32)});
 }
 return out;
}
/** Follow cursor pagination (max 100 per page). `get` performs one authorized, budgeted request. */
export async function fetchAllPages<T>(get:(cursor:string|null)=>Promise<{data:T[];meta?:{next_cursor?:number|string|null}}>,maxPages=20):Promise<T[]>{
 const out:T[]=[];let cursor:string|null=null;
 for(let i=0;i<maxPages;i++){
  const page:{data:T[];meta?:{next_cursor?:number|string|null}}=await get(cursor);
  out.push(...(page.data||[]));
  const next=page.meta?.next_cursor;
  if(next===undefined||next===null||next==="")return out;
  cursor=String(next);
 }
 throw new Error("Injury feed exceeded page limit");
}
