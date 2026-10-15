import {runScheduledSport} from "../../lib/persistence/scheduleRun";

/** NFL only, staggered every three hours to stay within Netlify's 30s scheduled-function limit. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledSport("NFL");
}
export const config={schedule:"15 */3 * * *"};
