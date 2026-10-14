import type {OddsProvider} from "./types";
import type {MarketQuote,MarketName} from "../contracts";
const teams:Record<string,[string,string][]>={
 NBA:[["Boston Celtics","New York Knicks"],["Los Angeles Lakers","Golden State Warriors"],["Milwaukee Bucks","Cleveland Cavaliers"]],
 NFL:[["Buffalo Bills","New York Jets"],["Dallas Cowboys","Philadelphia Eagles"],["Kansas City Chiefs","Denver Broncos"]],
 NHL:[["Boston Bruins","New York Rangers"],["Toronto Maple Leafs","Montreal Canadiens"],["Vegas Golden Knights","Edmonton Oilers"]],
 MLB:[["Boston Red Sox","New York Yankees"],["Los Angeles Dodgers","San Diego Padres"],["Chicago Cubs","St. Louis Cardinals"]]
};
const shape:Record<string,{spread:number;total:number}>={NBA:{spread:-4.5,total:218.5},NFL:{spread:-3.5,total:43.5},NHL:{spread:-1.5,total:5.5},MLB:{spread:-1.5,total:7.5}};
const books=["Northstar","Metro","Prime"];
export const mockProvider:OddsProvider={name:"controlled-demo",mode:"simulated",async health(){return{name:this.name,mode:this.mode,healthy:true,checkedAt:new Date().toISOString(),message:"Controlled development feed"}},async getMarkets(sport){const now=new Date();const games=teams[sport]||teams.NBA;const out:MarketQuote[]=[];const spec=shape[sport]||shape.NBA;games.forEach(([away,home],gi)=>{const eventId=sport.toLowerCase()+"-"+(gi+1);const startTime=new Date(now.getTime()+(gi+1)*3600000).toISOString();(["moneyline","spread","total"] as MarketName[]).forEach((market,mi)=>books.forEach((book,bi)=>{const base=-118+gi*7+mi*5+bi*4;const selection=market==="total"?"Over":home;const line=market==="spread"?(sport==="NHL"||sport==="MLB"?spec.spread:spec.spread+gi):market==="total"?spec.total+gi*(sport==="NHL"||sport==="MLB"?1:2):undefined;out.push({eventId,sport,market,selection,line,price:base,book,updatedAt:now.toISOString(),state:"simulated",away,home,startTime})}))});return out}};
