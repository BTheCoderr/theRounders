import {runScheduledBacktest} from "../../lib/persistence/scheduleRun";

/** Weekly Monday MLB walk-forward backtest and promotion gate. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledBacktest("MLB");
}
export const config={schedule:"50 12 * * 1"};
