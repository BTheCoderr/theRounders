import {runScheduledPredictions} from "../../lib/persistence/scheduleRun";

/** NFL pregame snapshots: the whole week on Tuesdays, then a two-day catch-up daily. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledPredictions("NFL");
}
export const config={schedule:"25 15 * * *"};
