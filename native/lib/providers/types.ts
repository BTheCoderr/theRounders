import type {MarketQuote} from "../contracts";
export type ProviderHealth={name:string;mode:"live"|"simulated";healthy:boolean;checkedAt:string;message?:string};
export interface OddsProvider{name:string;mode:"live"|"simulated";getMarkets(sport:string):Promise<MarketQuote[]>;health():Promise<ProviderHealth>}
