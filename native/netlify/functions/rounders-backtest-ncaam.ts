import {runScheduledBacktest} from "../../lib/persistence/scheduleRun";

/** Weekly Monday college basketball walk-forward backtest and promotion gate. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledBacktest("NCAAM");
}
export const config={schedule:"35 13 * * 1"};
