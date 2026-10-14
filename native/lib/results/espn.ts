import type {TeamGame} from "../ratings";

export type ResultsSource="external"|"simulated";
export type ResultsBatch={games:TeamGame[];source:ResultsSource;provider:string;fetchedAt:string;message?:string};

const league:Record<string,[string,string]>={
 NBA:["basketball","nba"],NFL:["football","nfl"],NHL:["hockey","nhl"],MLB:["baseball","mlb"]
};
type Competitor={homeAway:"home"|"away";score?:string;team?:{displayName?:string;abbreviation?:string}};
type Event={date?:string;status?:{type?:{completed?:boolean}};competitions?:Array<{competitors?:Competitor[]}>};

export async function getEspnResults(sport:string):Promise<ResultsBatch>{
 const pair=league[sport.toUpperCase()]; if(!pair)throw new Error("Unsupported sport");
 const [kind,slug]=pair,year=new Date().getUTCFullYear();
 const url=`https://site.api.espn.com/apis/site/v2/sports/${kind}/${slug}/scoreboard?dates=${year}&limit=1000`;
 const response=await fetch(url,{next:{revalidate:3600}});
 if(!response.ok)throw new Error(`Results provider returned ${response.status}`);
 const json=await response.json() as {events?:Event[]};
 const games=completedTeamGames(json.events||[]);
 if(!games.length)throw new Error("No completed games returned");
 return{games,source:"external",provider:"ESPN scoreboard",fetchedAt:new Date().toISOString(),message:"Public-facing scoreboard source; replaceable provider boundary"};
}

// The Odds API supplies full team names. Prefer ESPN's full display name
// over abbreviations so live matchup ratings can actually match market teams.
export function completedTeamGames(events:Event[]):TeamGame[]{
 const games:TeamGame[]=[];
 for(const event of events){
  if(!event.status?.type?.completed)continue;
  const competitors=event.competitions?.[0]?.competitors||[];
  const home=competitors.find(c=>c.homeAway==="home"),away=competitors.find(c=>c.homeAway==="away");
  const ht=home?.team?.displayName?.trim()||home?.team?.abbreviation?.trim();
  const at=away?.team?.displayName?.trim()||away?.team?.abbreviation?.trim();
  const hs=Number(home?.score),as=Number(away?.score);
  if(!ht||!at||ht===at||home?.score===undefined||away?.score===undefined||!Number.isFinite(hs)||!Number.isFinite(as))continue;
  const date=event.date||new Date().toISOString();
  games.push({date,team:ht,opponent:at,teamScore:hs,opponentScore:as,location:"home"});
  games.push({date,team:at,opponent:ht,teamScore:as,opponentScore:hs,location:"away"});
 }
 return games;
}
