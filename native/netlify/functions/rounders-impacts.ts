import {runScheduledImpacts} from "../../lib/persistence/scheduleRun";

/** Daily player game logs and impact ratings; no-op until enabled. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledImpacts();
}
export const config={schedule:"15 10 * * *"};
