import AsyncStorage from "@react-native-async-storage/async-storage";
import type {Quote} from "./markets";
const KEY="therounders.paper.v1";
export type PaperEntry={id:string;quote:Quote;stake:number;status:"pending"|"won"|"lost"|"push";placedAt:string};
export function validStake(value:number){return Number.isFinite(value)&&value>=1&&value<=100000;}
export async function loadPaper():Promise<PaperEntry[]>{
 try{const raw=await AsyncStorage.getItem(KEY);const arr=raw?JSON.parse(raw):[];return Array.isArray(arr)?arr.filter((e):e is PaperEntry=>e&&typeof e.id==="string"&&validStake(e.stake)&&["pending","won","lost","push"].includes(e.status)).slice(0,500):[]}
 catch{return []}
}
export async function writePaper(bets:PaperEntry[]):Promise<void>{await AsyncStorage.setItem(KEY,JSON.stringify(bets.slice(0,500)))}
export function profit(bet:PaperEntry):number{
 if(bet.status==="pending"||bet.status==="push")return 0;
 if(bet.status==="lost")return -bet.stake;
 return bet.quote.price>0?bet.stake*bet.quote.price/100:bet.stake*100/Math.abs(bet.quote.price);
}
