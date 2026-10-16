import {runScheduledEvaluation} from "../../lib/persistence/scheduleRun";

/** Model scoring runs independently of the short historical-data import window. */
export default async function handler(_request:Request):Promise<Response>{
 return runScheduledEvaluation("MLB");
}
export const config={schedule:"45 14 * * *"};
