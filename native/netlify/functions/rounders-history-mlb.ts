import {runScheduledSport} from "../../lib/persistence/scheduleRun";

/** MLB only, staggered every three hours to stay within Netlify's 30s scheduled-function limit. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledSport("MLB");
}
export const config={schedule:"45 */3 * * *"};
