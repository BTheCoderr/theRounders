import {runScheduledInjuries} from "../../lib/persistence/scheduleRun";

/** NBA/NFL injury reports and injury-adjusted v4 forecasts; no-op until enabled. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledInjuries();
}
export const config={schedule:"45 * * * *"};
