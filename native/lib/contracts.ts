export type DataState="live"|"model"|"simulated";
export type MarketName="moneyline"|"spread"|"total";
export type MarketQuote={eventId:string;sport:string;market:MarketName;selection:string;line?:number;price:number;book:string;updatedAt:string;state:DataState;away:string;home:string;startTime:string};
export type SharpSignal={eventId:string;kind:"steam"|"rlm";confidence:number;movement:number;detectedAt:string;state:"model"};
export type PaperBet={id:string;eventId:string;sport:string;matchup:string;market:MarketName;selection:string;line?:number;price:number;book:string;stake:number;status:"pending"|"won"|"lost"|"push";placedAt:string;dataState:DataState};
