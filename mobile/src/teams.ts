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
const NHL:Record<string,Team>={
 "Anaheim Ducks":{abbr:"ANA",color:"#F47A38"},"Boston Bruins":{abbr:"BOS",color:"#FFB81C"},"Buffalo Sabres":{abbr:"BUF",color:"#003087"},
 "Calgary Flames":{abbr:"CGY",color:"#C8102E"},"Carolina Hurricanes":{abbr:"CAR",color:"#CE1126"},"Chicago Blackhawks":{abbr:"CHI",color:"#CF0A2C"},
 "Colorado Avalanche":{abbr:"COL",color:"#6F263D"},"Columbus Blue Jackets":{abbr:"CBJ",color:"#002654"},"Dallas Stars":{abbr:"DAL",color:"#006847"},
 "Detroit Red Wings":{abbr:"DET",color:"#CE1126"},"Edmonton Oilers":{abbr:"EDM",color:"#041E42"},"Florida Panthers":{abbr:"FLA",color:"#C8102E"},
 "Los Angeles Kings":{abbr:"LA",color:"#111111"},"Minnesota Wild":{abbr:"MIN",color:"#154734"},"Montreal Canadiens":{abbr:"MTL",color:"#AF1E2D"},
 "Montréal Canadiens":{abbr:"MTL",color:"#AF1E2D"},"Nashville Predators":{abbr:"NSH",color:"#FFB81C"},"New Jersey Devils":{abbr:"NJ",color:"#CE1126"},
 "New York Islanders":{abbr:"NYI",color:"#00539B"},"New York Rangers":{abbr:"NYR",color:"#0038A8"},"Ottawa Senators":{abbr:"OTT",color:"#C52032"},
 "Philadelphia Flyers":{abbr:"PHI",color:"#F74902"},"Pittsburgh Penguins":{abbr:"PIT",color:"#FCB514"},"San Jose Sharks":{abbr:"SJ",color:"#006D75"},
 "Seattle Kraken":{abbr:"SEA",color:"#001628"},"St. Louis Blues":{abbr:"STL",color:"#002F87"},"Tampa Bay Lightning":{abbr:"TB",color:"#002868"},
 "Toronto Maple Leafs":{abbr:"TOR",color:"#00205B"},"Utah Mammoth":{abbr:"UTA",color:"#6CACE4"},"Utah Hockey Club":{abbr:"UTA",color:"#6CACE4"},
 "Vancouver Canucks":{abbr:"VAN",color:"#00205B"},"Vegas Golden Knights":{abbr:"VGK",color:"#B4975A"},"Washington Capitals":{abbr:"WSH",color:"#C8102E"},
 "Winnipeg Jets":{abbr:"WPG",color:"#041E42"}
};
const MLB:Record<string,Team>={
 "Arizona Diamondbacks":{abbr:"ARI",color:"#A71930"},"Atlanta Braves":{abbr:"ATL",color:"#CE1141"},"Baltimore Orioles":{abbr:"BAL",color:"#DF4601"},
 "Boston Red Sox":{abbr:"BOS",color:"#BD3039"},"Chicago Cubs":{abbr:"CHC",color:"#0E3386"},"Chicago White Sox":{abbr:"CHW",color:"#27251F"},
 "Cincinnati Reds":{abbr:"CIN",color:"#C6011F"},"Cleveland Guardians":{abbr:"CLE",color:"#00385D"},"Colorado Rockies":{abbr:"COL",color:"#333366"},
 "Detroit Tigers":{abbr:"DET",color:"#0C2340"},"Houston Astros":{abbr:"HOU",color:"#EB6E1F"},"Kansas City Royals":{abbr:"KC",color:"#004687"},
 "Los Angeles Angels":{abbr:"LAA",color:"#BA0021"},"Los Angeles Dodgers":{abbr:"LAD",color:"#005A9C"},"Miami Marlins":{abbr:"MIA",color:"#00A3E0"},
 "Milwaukee Brewers":{abbr:"MIL",color:"#12284B"},"Minnesota Twins":{abbr:"MIN",color:"#002B5C"},"New York Mets":{abbr:"NYM",color:"#002D72"},
 "New York Yankees":{abbr:"NYY",color:"#0C2340"},"Athletics":{abbr:"ATH",color:"#003831"},"Oakland Athletics":{abbr:"OAK",color:"#003831"},
 "Philadelphia Phillies":{abbr:"PHI",color:"#E81828"},"Pittsburgh Pirates":{abbr:"PIT",color:"#27251F"},"San Diego Padres":{abbr:"SD",color:"#2F241D"},
 "San Francisco Giants":{abbr:"SF",color:"#FD5A1E"},"Seattle Mariners":{abbr:"SEA",color:"#0C2C56"},"St. Louis Cardinals":{abbr:"STL",color:"#C41E3A"},
 "Tampa Bay Rays":{abbr:"TB",color:"#092C5C"},"Texas Rangers":{abbr:"TEX",color:"#003278"},"Toronto Blue Jays":{abbr:"TOR",color:"#134A8E"},
 "Washington Nationals":{abbr:"WSH",color:"#AB0003"}
};
const COLLEGE=new Set(["NCAAM","NCAAF"]);
const BY_SPORT:Record<string,Record<string,Team>>={NBA,NFL,NHL,MLB};
export function team(sport:string,name:string):Team{
 const hit=BY_SPORT[sport]?.[name];
 if(hit)return hit;
 const words=name.replace(/[^A-Za-z0-9&' ]/g," ").split(/\s+/).filter(Boolean);
 // College: the school's first word ("DUKE", "OHIO"); otherwise initials. Neutral color, no logos.
 const abbr=COLLEGE.has(sport)?(words[0]||name).slice(0,4):(words.length>1?words.map(w=>w[0]).join(""):name).slice(0,3);
 return {abbr:abbr.toUpperCase(),color:COLLEGE.has(sport)?"#2B4B7C":"#334A6E"};
}
const TWO_WORD=/(Trail Blazers|Red Sox|White Sox|Blue Jays|Maple Leafs|Golden Knights|Blue Jackets|Red Wings)$/;
/** Nickname for compact rows: "Boston Celtics" -> "Celtics". College teams keep their full name (school + mascot). */
export function nickname(name:string,sport?:string):string{
 if(sport&&COLLEGE.has(sport))return name;
 const two=name.match(TWO_WORD);if(two)return two[1];
 const w=name.split(/\s+/);return w.length>1?w[w.length-1]:name;
}
/** Readable text color on a badge background. */
export function onColor(hex:string):string{
 const n=parseInt(hex.slice(1),16),r=n>>16&255,g=n>>8&255,b=n&255;
 return (0.299*r+0.587*g+0.114*b)>165?"#081429":"#FFFFFF";
}
