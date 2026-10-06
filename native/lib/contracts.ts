export type DataState="live"|"model"|"simulated";
export type MarketQuote={eventId:string;sport:string;market:string;selection:string;price:number;book:string;updatedAt:string;state:DataState};
export type SharpSignal={eventId:string;kind:"steam"|"rlm";confidence:number;movement:number;detectedAt:string;state:"model"};
