import {runScheduledPredictions} from "../../lib/persistence/scheduleRun";

/** College football snapshots: the coming week on Tuesdays, two-day catch-up otherwise. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledPredictions("NCAAF");
}
export const config={schedule:"30 15 * * *"};
