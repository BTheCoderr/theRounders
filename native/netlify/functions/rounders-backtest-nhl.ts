import {runScheduledBacktest} from "../../lib/persistence/scheduleRun";

/** Weekly Monday NHL walk-forward backtest and promotion gate. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledBacktest("NHL");
}
export const config={schedule:"35 12 * * 1"};
