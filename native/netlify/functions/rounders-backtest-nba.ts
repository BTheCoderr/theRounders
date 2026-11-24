import {runScheduledBacktest} from "../../lib/persistence/scheduleRun";

/** Daily NBA walk-forward backtest and promotion gate. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledBacktest("NBA");
}
export const config={schedule:"5 13 * * *"};
