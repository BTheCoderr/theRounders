import {runScheduledBacktest} from "../../lib/persistence/scheduleRun";

/** Daily NFL walk-forward backtest and promotion gate. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledBacktest("NFL");
}
export const config={schedule:"20 13 * * *"};
