import {runScheduledSport} from "../../lib/persistence/scheduleRun";

/** College basketball archive import: every 20 minutes so the multi-season backfill finishes within a day. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledSport("NCAAM");
}
export const config={schedule:"5,25,45 * * * *"};
