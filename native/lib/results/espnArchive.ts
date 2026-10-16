/** Provider-normalized, explicitly regular-season final scores for the research archive.
 * Unofficial ESPN scoreboard shape: no official data completeness or reuse license implied.
 */
export type ArchivedEvent={
 eventId:string;date:string;season:number;
 homeId:string;awayId:string;home:string;away:string;
 homeScore:number;awayScore:number;neutral:boolean
};
export type ArchiveMonth={
 games:ArchivedEvent[];
 excluded:number;unknown:number;completedSeen:number;
};
const league:Record<string,[string,string]>={
 NBA:["basketball","nba"],NFL:["football","nfl"],NHL:["hockey","nhl"],MLB:["baseball","mlb"]
};
type Competitor={id?:string;homeAway?:string;score?:string;team?:{id?:string;displayName?:string;abbreviation?:string}};
type Event={
 id?:string;date?:string;season?:{type?:number|string;year?:number;slug?:string};
 status?:{type?:{completed?:boolean}};
 competitions?:Array<{neutralSite?:boolean;competitors?:Competitor[]}>
};
export function parseArchiveMonth(events:Event[],yearMonth:string):ArchiveMonth{
 const games:ArchivedEvent[]=[];
 let excluded=0,unknown=0,completedSeen=0;
 const seen=new Set<string>();
 for(const e of events){
  if(!e?.status?.type?.completed)continue;
  if(!e.date||e.date.slice(0,7).replace("-","")!==yearMonth)continue;
  completedSeen++;
  const phase=Number(e.season?.type);
  if(!Number.isInteger(phase)||phase<1){unknown++;continue;}
  if(phase!==2){excluded++;continue;} // 1=preseason, 3=postseason, 4=offseason, etc.
  const competition=e.competitions?.[0];
  const home=competition?.competitors?.find(t=>t.homeAway==="home");
  const away=competition?.competitors?.find(t=>t.homeAway==="away");
  const homeId=String(home?.team?.id||home?.id||"").trim();
  const awayId=String(away?.team?.id||away?.id||"").trim();
  const hname=(home?.team?.displayName||home?.team?.abbreviation||"").trim();
  const aname=(away?.team?.displayName||away?.team?.abbreviation||"").trim();
  const hs=Number(home?.score),as=Number(away?.score);
  const eventId=String(e.id||"").trim();
  const season=Number(e.season?.year);
  if(!eventId||!homeId||!awayId||homeId===awayId||
     !hname||!aname||hname===aname||
     home?.score===undefined||away?.score===undefined||
     !Number.isInteger(hs)||!Number.isInteger(as)||hs<0||as<0||
     !Number.isInteger(season)||season<1900||season>2200||
     !Number.isFinite(Date.parse(e.date||""))){
    unknown++;continue;
  }
  if(seen.has(eventId))continue;
  seen.add(eventId);
  games.push({eventId,date:new Date(e.date).toISOString(),season,
   homeId,awayId,home:hname,away:aname,homeScore:hs,awayScore:as,
   neutral:competition?.neutralSite===true});
 }
 return {games,excluded,unknown,completedSeen};
}
export async function fetchRegularArchiveMonth(sport:string,yearMonth:string):Promise<ArchiveMonth>{
 const pair=league[sport.toUpperCase()];
 if(!pair||!/^20\d{2}(0[1-9]|1[0-2])$/.test(yearMonth))
  throw new Error("Invalid sport or month");
 const [kind,slug]=pair;
 const response=await fetch(`https://site.api.espn.com/apis/site/v2/sports/${kind}/${slug}/scoreboard?dates=${yearMonth}&limit=1000`,{
  signal:AbortSignal.timeout(12000),next:{revalidate:86400}
 });
 if(!response.ok)throw new Error("Archive provider HTTP "+response.status);
 const data=await response.json() as {events?:Event[]};
 if(!Array.isArray(data.events)||data.events.length>=1000)
  throw new Error("Archive provider missing/truncated event list");
 const parsed=parseArchiveMonth(data.events,yearMonth);
 if(parsed.unknown>0)
  throw new Error(`Archive provider had ${parsed.unknown} completed regular/unknown games without trustworthy phase or identity`);
 return parsed;
}
