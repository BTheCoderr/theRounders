/**
 * Every per-sport setting in one place. Values are documented priors chosen before
 * evaluation, not tuned on the backtest window; win-probability spread (σ) is
 * re-learned from out-of-sample errors (engine/calibration.ts).
 */
export type Sport="NBA"|"NFL"|"NCAAM"|"NCAAF"|"NHL"|"MLB";
export const ALL_SPORTS:readonly Sport[]=["NBA","NFL","NCAAM","NCAAF","NHL","MLB"];
export const isSport=(s:string):s is Sport=>(ALL_SPORTS as readonly string[]).includes(s);

export type SportConfig={
 label:string;short:string;unit:"pts"|"goals"|"runs";
 /** ESPN site API path and, for college, the division group (50 = Division I MBB, 80 = FBS). */
 espn:{kind:string;slug:string;groups?:string};
 odds:string;
 homeAdvantage:number;marginSigma:number;eloPointScale:number;v1Baseline:number;
 power:{ridge:number;halfLifeDays:number;marginCap:number};
 totals:{halfLifeDays:number;ridge:number};
 rpi:{halfLifeDays:number;ridge:number;huberDelta:number;homeRidge:number};
 v3:{retention:number;restCapDays:number;restRidge:number};
 gateGames:number;calibrationGames:number;minTrainGames:number;backtestWeeks:number;
 /** daily = predict the next ~day; weekly = full week on Tuesdays, two-day catch-up otherwise. */
 slate:"daily"|"weekly";
 /** Season labeled by the calendar year it starts (false) or the calendar year itself (MLB). */
 calendarSeason:boolean;
 /** Regular season ends around this month/day of the following (or, for calendar seasons, same) year. */
 seasonEnd:{month:number;day:number;nextYear:boolean};
 /** Teams with fewer archived games are exhibition or lower-division opponents, not modeled. */
 minFranchiseGames:number;
 /** ESPN caps events per request (`pageLimit`; college rejects more than 500): fetch in chunks this many days long. */
 chunkDays:number;pageLimit:number;
 historyMonths:number;maxArchivePages:number;
 expected:{teams:number;regularSeasonGames:number};
 /** Calendar months (1-12) that can contain regular-season games (deep-history walk skips the rest). */
 seasonMonths:number[];
 /** Minimum games in one season for a team to appear in that season's history table. */
 seasonMinGames:number;
};

export const SPORT_CONFIG:Record<Sport,SportConfig>={
 NBA:{seasonMonths:[10,11,12,1,2,3,4,7,8],seasonMinGames:20,label:"NBA",short:"NBA",unit:"pts",espn:{kind:"basketball",slug:"nba"},odds:"basketball_nba",
  homeAdvantage:2.2,marginSigma:12,eloPointScale:0.04,v1Baseline:112,
  power:{ridge:1.25,halfLifeDays:45,marginCap:25},totals:{halfLifeDays:45,ridge:4},
  rpi:{halfLifeDays:45,ridge:1.25,huberDelta:12,homeRidge:20},v3:{retention:0.5,restCapDays:3,restRidge:200},
  gateGames:600,calibrationGames:300,minTrainGames:300,backtestWeeks:80,slate:"daily",calendarSeason:false,
  seasonEnd:{month:4,day:15,nextYear:true},minFranchiseGames:20,chunkDays:31,pageLimit:1000,historyMonths:73,maxArchivePages:22,
  expected:{teams:30,regularSeasonGames:1230}},
 NFL:{seasonMonths:[9,10,11,12,1],seasonMinGames:8,label:"NFL",short:"NFL",unit:"pts",espn:{kind:"football",slug:"nfl"},odds:"americanfootball_nfl",
  homeAdvantage:2.2,marginSigma:13.5,eloPointScale:0.03,v1Baseline:23,
  power:{ridge:1.25,halfLifeDays:60,marginCap:17},totals:{halfLifeDays:90,ridge:2},
  rpi:{halfLifeDays:60,ridge:1.25,huberDelta:9,homeRidge:20},v3:{retention:0.5,restCapDays:14,restRidge:40},
  gateGames:250,calibrationGames:150,minTrainGames:120,backtestWeeks:156,slate:"weekly",calendarSeason:false,
  seasonEnd:{month:1,day:12,nextYear:true},minFranchiseGames:20,chunkDays:62,pageLimit:1000,historyMonths:73,maxArchivePages:22,
  expected:{teams:32,regularSeasonGames:272}},
 NCAAM:{seasonMonths:[11,12,1,2,3],seasonMinGames:10,label:"College Basketball",short:"CBB",unit:"pts",espn:{kind:"basketball",slug:"mens-college-basketball",groups:"50"},odds:"basketball_ncaab",
  homeAdvantage:3,marginSigma:11,eloPointScale:0.04,v1Baseline:72,
  power:{ridge:1.25,halfLifeDays:60,marginCap:25},totals:{halfLifeDays:60,ridge:4},
  rpi:{halfLifeDays:60,ridge:1.25,huberDelta:12,homeRidge:20},v3:{retention:0.4,restCapDays:4,restRidge:200},
  gateGames:600,calibrationGames:300,minTrainGames:1500,backtestWeeks:20,slate:"daily",calendarSeason:false,
  seasonEnd:{month:3,day:16,nextYear:true},minFranchiseGames:40,chunkDays:1,pageLimit:500,historyMonths:40,maxArchivePages:24,
  expected:{teams:364,regularSeasonGames:5600}},
 NCAAF:{seasonMonths:[8,9,10,11,12],seasonMinGames:6,label:"College Football",short:"CFB",unit:"pts",espn:{kind:"football",slug:"college-football",groups:"80"},odds:"americanfootball_ncaaf",
  homeAdvantage:2.5,marginSigma:16,eloPointScale:0.025,v1Baseline:28,
  power:{ridge:1.25,halfLifeDays:90,marginCap:28},totals:{halfLifeDays:90,ridge:2},
  rpi:{halfLifeDays:90,ridge:1.25,huberDelta:14,homeRidge:20},v3:{retention:0.4,restCapDays:14,restRidge:40},
  gateGames:250,calibrationGames:150,minTrainGames:300,backtestWeeks:120,slate:"weekly",calendarSeason:false,
  seasonEnd:{month:12,day:14,nextYear:false},minFranchiseGames:25,chunkDays:1,pageLimit:500,historyMonths:73,maxArchivePages:12,
  expected:{teams:136,regularSeasonGames:800}},
 NHL:{seasonMonths:[10,11,12,1,2,3,4],seasonMinGames:20,label:"NHL",short:"NHL",unit:"goals",espn:{kind:"hockey",slug:"nhl"},odds:"icehockey_nhl",
  homeAdvantage:0.18,marginSigma:2.4,eloPointScale:0.0035,v1Baseline:3.1,
  power:{ridge:1.25,halfLifeDays:50,marginCap:3},totals:{halfLifeDays:50,ridge:6},
  rpi:{halfLifeDays:50,ridge:1.25,huberDelta:1.5,homeRidge:20},v3:{retention:0.5,restCapDays:3,restRidge:200},
  gateGames:600,calibrationGames:300,minTrainGames:300,backtestWeeks:80,slate:"daily",calendarSeason:false,
  seasonEnd:{month:4,day:18,nextYear:true},minFranchiseGames:20,chunkDays:31,pageLimit:1000,historyMonths:73,maxArchivePages:22,
  expected:{teams:32,regularSeasonGames:1312}},
 MLB:{seasonMonths:[3,4,5,6,7,8,9,10],seasonMinGames:20,label:"MLB",short:"MLB",unit:"runs",espn:{kind:"baseball",slug:"mlb"},odds:"baseball_mlb",
  homeAdvantage:0.25,marginSigma:4.4,eloPointScale:0.005,v1Baseline:4.5,
  power:{ridge:1.25,halfLifeDays:35,marginCap:5},totals:{halfLifeDays:35,ridge:6},
  rpi:{halfLifeDays:35,ridge:1.25,huberDelta:2.5,homeRidge:20},v3:{retention:0.5,restCapDays:3,restRidge:200},
  gateGames:600,calibrationGames:300,minTrainGames:300,backtestWeeks:60,slate:"daily",calendarSeason:true,
  seasonEnd:{month:9,day:30,nextYear:false},minFranchiseGames:20,chunkDays:20,pageLimit:1000,historyMonths:73,maxArchivePages:22,
  expected:{teams:30,regularSeasonGames:2430}}
};

/** Season label for a game date: start year (Jul+ belongs to the new season) or, for MLB, the calendar year. */
export function seasonFor(sport:Sport|undefined,date:string|number):number{
 const d=new Date(date);const y=d.getUTCFullYear(),m=d.getUTCMonth();
 return sport&&SPORT_CONFIG[sport].calendarSeason?y:m>=6?y:y-1;
}
/** Approximate end of the regular season that contains `season`. */
export function seasonEndDate(sport:Sport,season:number):Date{
 const e=SPORT_CONFIG[sport].seasonEnd;
 return new Date(Date.UTC(season+(e.nextYear?1:0),e.month-1,e.day,23,59));
}
/** ESPN scoreboard URL for an inclusive date range (YYYYMMDD or YYYYMM). */
export function espnScoreboardUrl(sport:Sport,dates:string){
 const {espn:{kind,slug,groups},pageLimit}=SPORT_CONFIG[sport];
 const [a,b]=dates.split("-");
 return `https://site.api.espn.com/apis/site/v2/sports/${kind}/${slug}/scoreboard?dates=${b&&a===b?a:dates}&limit=${pageLimit}${groups?"&groups="+groups:""}`;
}
/** Run async tasks with at most `n` in flight (keeps busy college months polite to the feed). */
export async function mapLimit<T,R>(items:T[],n:number,fn:(x:T)=>Promise<R>):Promise<R[]>{
 const out:R[]=new Array(items.length);let i=0;
 await Promise.all([...Array(Math.min(n,items.length))].map(async()=>{while(i<items.length){const k=i++;out[k]=await fn(items[k]);}}));
 return out;
}
