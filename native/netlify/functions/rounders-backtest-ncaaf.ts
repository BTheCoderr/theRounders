import {runScheduledBacktest} from "../../lib/persistence/scheduleRun";

/** Daily college football walk-forward backtest and promotion gate. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledBacktest("NCAAF");
}
export const config={schedule:"50 13 * * *"};
