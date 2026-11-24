/** Response shapes of the public NBA/NFL APIs, shared by web components. */
export type ProductSport="NBA"|"NFL";
export const PRODUCT_SPORTS:readonly ProductSport[]=["NBA","NFL"];

export type PredictionView={
 eventId:string;startsAt:string;home:string;away:string;neutral:boolean;
 predictedAt:string;modelVersion:string;totalsModel:string;
 projectedWinner:string;homeWinProbability:number;
 /** Null when the field is reserved for a paid plan (see `locked`). */
 projectedHome:number|null;projectedAway:number|null;projectedSpreadHome:number|null;projectedTotal:number|null;
 market:{spreadHome:number|null;total:number|null;source:string;state:"live"}|null;
 trainingGames:number;trainingThrough:string|null;
 status:"pending"|"graded"|"void";final:{home:number;away:number}|null;
 locked?:string[];
};
export type PredictionsResponse={
 sport:ProductSport;model:string;modelLabel?:string;ready:boolean;reason?:string;
 predictions:PredictionView[];notice?:string;plan?:string;upgrade?:string|null;
};
export type Summary={
 games:number;decided:number;winnerAccuracy:number|null;brierScore:number|null;logLoss:number|null;
 marginMAE:number|null;marginRMSE:number|null;marginBias:number|null;
 totalGames:number;totalMAE:number|null;totalBias:number|null;
 calibration:Array<{from:number;to:number;forecasts:number;meanForecast:number|null;observedRate:number|null}>;
 againstSpread:{games:number;wins:number;losses:number;pushes:number;winRate:number|null};
 againstTotal:{games:number;wins:number;losses:number;pushes:number;winRate:number|null};
};
export type PerformanceResponse={
 sport:ProductSport;champion:string;championLabel?:string;ready:boolean;reason?:string;
 live?:Array<{model:string;label:string;champion:boolean;from:string|null;through:string|null;summary:Summary}>;
 backtest?:null|{runDay:string;engineRevision:string;dataSource:string;historicalGames:number;evaluatedGames:number;evaluatedWeeks:number;
  seasons:number[];from:string|null;through:string|null;
  models:Array<{model:string;label:string;summary:Summary}>;
  totals:{model:string;summary:{games:number;mae:number|null;bias:number|null};baseline:{games:number;mae:number|null;bias:number|null}};
  promotion:Array<{champion:string;challenger:string;recommend:boolean;games:number;seasons:number;maeDifference:number|null;standardError:number|null;brierDifference:number|null;reasons:string[]}>};
 notes?:string[];
};
export const pct=(x:number|null|undefined,d=1)=>x===null||x===undefined?"—":(x*100).toFixed(d)+"%";
export const num=(x:number|null|undefined,d=2)=>x===null||x===undefined?"—":x.toFixed(d);
export const signed=(x:number)=>(x>0?"+":"")+x.toFixed(1);
export const kickoff=(iso:string)=>new Date(iso).toLocaleString([],{weekday:"short",month:"short",day:"numeric",hour:"numeric",minute:"2-digit"});
