import type {OddsProvider,ProviderHealth} from "./types";
import type {MarketQuote} from "../contracts";
export const liveProvider:OddsProvider={name:"live-odds",mode:"live",async health():Promise<ProviderHealth>{const configured=Boolean(process.env.ODDS_API_KEY);return{name:this.name,mode:this.mode,healthy:configured,checkedAt:new Date().toISOString(),message:configured?"Live provider configured":"Live provider not configured"}},async getMarkets(_sport:string):Promise<MarketQuote[]>{throw new Error("Live adapter transport not configured")}};
