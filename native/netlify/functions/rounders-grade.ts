import {runScheduledGrading} from "../../lib/persistence/scheduleRun";

/** Grades finished predictions for every sport hourly. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledGrading();
}
export const config={schedule:"0 * * * *"};
