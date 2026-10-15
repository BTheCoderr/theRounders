import {runScheduledSport} from "../../lib/persistence/scheduleRun";

/** NHL only, staggered every three hours to stay within Netlify's 30s scheduled-function limit. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledSport("NHL");
}
export const config={schedule:"30 */3 * * *"};
