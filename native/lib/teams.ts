/**
 * Team abbreviations and primary colors for badges. Text only: no logos or
 * trademarked artwork. Unknown names fall back to initials on a neutral color.
 */
type Team={abbr:string;color:string};
const NBA:Record<string,Team>={
 "Atlanta Hawks":{abbr:"ATL",color:"#C8102E"},"Boston Celtics":{abbr:"BOS",color:"#007A33"},
 "Brooklyn Nets":{abbr:"BKN",color:"#4B4B4B"},"Charlotte Hornets":{abbr:"CHA",color:"#1D1160"},
 "Chicago Bulls":{abbr:"CHI",color:"#CE1141"},"Cleveland Cavaliers":{abbr:"CLE",color:"#860038"},
 "Dallas Mavericks":{abbr:"DAL",color:"#00538C"},"Denver Nuggets":{abbr:"DEN",color:"#0E2240"},
 "Detroit Pistons":{abbr:"DET",color:"#C8102E"},"Golden State Warriors":{abbr:"GSW",color:"#1D428A"},
 "Houston Rockets":{abbr:"HOU",color:"#CE1141"},"Indiana Pacers":{abbr:"IND",color:"#002D62"},
 "LA Clippers":{abbr:"LAC",color:"#C8102E"},"Los Angeles Clippers":{abbr:"LAC",color:"#C8102E"},
 "Los Angeles Lakers":{abbr:"LAL",color:"#552583"},"Memphis Grizzlies":{abbr:"MEM",color:"#5D76A9"},
 "Miami Heat":{abbr:"MIA",color:"#98002E"},"Milwaukee Bucks":{abbr:"MIL",color:"#00471B"},
 "Minnesota Timberwolves":{abbr:"MIN",color:"#236192"},"New Orleans Pelicans":{abbr:"NOP",color:"#0C2340"},
 "New York Knicks":{abbr:"NYK",color:"#006BB6"},"Oklahoma City Thunder":{abbr:"OKC",color:"#007AC1"},
 "Orlando Magic":{abbr:"ORL",color:"#0077C0"},"Philadelphia 76ers":{abbr:"PHI",color:"#006BB6"},
 "Phoenix Suns":{abbr:"PHX",color:"#E56020"},"Portland Trail Blazers":{abbr:"POR",color:"#E03A3E"},
 "Sacramento Kings":{abbr:"SAC",color:"#5A2D81"},"San Antonio Spurs":{abbr:"SAS",color:"#8A8D8F"},
 "Toronto Raptors":{abbr:"TOR",color:"#CE1141"},"Utah Jazz":{abbr:"UTA",color:"#002B5C"},
 "Washington Wizards":{abbr:"WAS",color:"#002B5C"}
};
const NFL:Record<string,Team>={
 "Arizona Cardinals":{abbr:"ARI",color:"#97233F"},"Atlanta Falcons":{abbr:"ATL",color:"#A71930"},
 "Baltimore Ravens":{abbr:"BAL",color:"#241773"},"Buffalo Bills":{abbr:"BUF",color:"#00338D"},
 "Carolina Panthers":{abbr:"CAR",color:"#0085CA"},"Chicago Bears":{abbr:"CHI",color:"#C83803"},
 "Cincinnati Bengals":{abbr:"CIN",color:"#FB4F14"},"Cleveland Browns":{abbr:"CLE",color:"#FF3C00"},
 "Dallas Cowboys":{abbr:"DAL",color:"#041E42"},"Denver Broncos":{abbr:"DEN",color:"#FB4F14"},
 "Detroit Lions":{abbr:"DET",color:"#0076B6"},"Green Bay Packers":{abbr:"GB",color:"#203731"},
 "Houston Texans":{abbr:"HOU",color:"#03202F"},"Indianapolis Colts":{abbr:"IND",color:"#002C5F"},
 "Jacksonville Jaguars":{abbr:"JAX",color:"#006778"},"Kansas City Chiefs":{abbr:"KC",color:"#E31837"},
 "Las Vegas Raiders":{abbr:"LV",color:"#4B4B4B"},"Los Angeles Chargers":{abbr:"LAC",color:"#0080C6"},
 "Los Angeles Rams":{abbr:"LAR",color:"#003594"},"Miami Dolphins":{abbr:"MIA",color:"#008E97"},
 "Minnesota Vikings":{abbr:"MIN",color:"#4F2683"},"New England Patriots":{abbr:"NE",color:"#002244"},
 "New Orleans Saints":{abbr:"NO",color:"#9F8958"},"New York Giants":{abbr:"NYG",color:"#0B2265"},
 "New York Jets":{abbr:"NYJ",color:"#125740"},"Philadelphia Eagles":{abbr:"PHI",color:"#004C54"},
 "Pittsburgh Steelers":{abbr:"PIT",color:"#FFB612"},"San Francisco 49ers":{abbr:"SF",color:"#AA0000"},
 "Seattle Seahawks":{abbr:"SEA",color:"#002244"},"Tampa Bay Buccaneers":{abbr:"TB",color:"#D50A0A"},
 "Tennessee Titans":{abbr:"TEN",color:"#4B92DB"},"Washington Commanders":{abbr:"WSH",color:"#5A1414"}
};
export function team(sport:string,name:string):Team{
 const hit=(sport==="NFL"?NFL:NBA)[name];
 if(hit)return hit;
 const words=name.split(/\s+/).filter(Boolean);
 return {abbr:(words.length>1?words.map(w=>w[0]).join(""):name).slice(0,3).toUpperCase(),color:"#334A6E"};
}
/** Nickname for compact rows: "Boston Celtics" -> "Celtics", "Portland Trail Blazers" -> "Trail Blazers". */
export function nickname(name:string):string{
 if(/Trail Blazers$/.test(name))return "Trail Blazers";
 const w=name.split(/\s+/);return w.length>1?w[w.length-1]:name;
}
/** Readable text color on a badge background. */
export function onColor(hex:string):string{
 const n=parseInt(hex.slice(1),16),r=n>>16&255,g=n>>8&255,b=n&255;
 return (0.299*r+0.587*g+0.114*b)>165?"#081429":"#FFFFFF";
}
