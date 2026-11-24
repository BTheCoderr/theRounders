import {runScheduledSport} from "../../lib/persistence/scheduleRun";

/** College football archive import: every 20 minutes during the initial backfill. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledSport("NCAAF");
}
export const config={schedule:"10,30,50 * * * *"};
