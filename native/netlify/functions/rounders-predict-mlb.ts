import {runScheduledPredictions} from "../../lib/persistence/scheduleRun";

/** MLB pregame snapshots for the next day's games (none in the offseason). */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledPredictions("MLB");
}
export const config={schedule:"40 15 * * *"};
