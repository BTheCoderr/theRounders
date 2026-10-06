import type {MarketQuote} from "../contracts";
export interface OddsProvider{name:string;getMarkets(sport:string):Promise<MarketQuote[]>}
