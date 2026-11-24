import {runScheduledGrading} from "../../lib/persistence/scheduleRun";

/** Grades finished NBA/NFL predictions every three hours. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledGrading();
}
export const config={schedule:"50 */3 * * *"};
