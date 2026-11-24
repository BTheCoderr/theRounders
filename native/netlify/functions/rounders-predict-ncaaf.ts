import {runScheduledPredictions} from "../../lib/persistence/scheduleRun";

/** Hourly: locks the first pregame prediction for each upcoming game in the window (idempotent). */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledPredictions("NCAAF");
}
export const config={schedule:"30 * * * *"};
