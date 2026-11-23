import {runScheduledPredictions} from "../../lib/persistence/scheduleRun";

/** NBA pregame snapshots for roughly the next day's games (UTC 15:20, before tip-offs). */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledPredictions("NBA");
}
export const config={schedule:"20 15 * * *"};
