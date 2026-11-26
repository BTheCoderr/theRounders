import {runScheduledOdds} from "../../lib/persistence/scheduleRun";

/** Odds capture (opening, updates and closing lines) within the spend budget; no-op until enabled. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledOdds();
}
export const config={schedule:"*/15 * * * *"};
