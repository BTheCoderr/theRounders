import {runScheduledPredictions} from "../../lib/persistence/scheduleRun";

/** NHL pregame snapshots for the next day's games. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledPredictions("NHL");
}
export const config={schedule:"35 15 * * *"};
