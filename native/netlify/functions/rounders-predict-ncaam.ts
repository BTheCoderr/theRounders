import {runScheduledPredictions} from "../../lib/persistence/scheduleRun";

/** College basketball pregame snapshots for the next day's games (UTC 15:10). */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledPredictions("NCAAM");
}
export const config={schedule:"10 15 * * *"};
