import {runScheduledBacktest} from "../../lib/persistence/scheduleRun";

/** Weekly Monday NBA walk-forward backtest and promotion gate. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledBacktest("NBA");
}
export const config={schedule:"5 13 * * 1"};
