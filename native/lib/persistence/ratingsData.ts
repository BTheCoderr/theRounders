import {uniqueCompletedGames} from "../powerRatings";
import {getVerifiedResearchGames} from "./history";
import type {EngineSport} from "../engine/models";

/** Completed, de-duplicated regular-season games from the verified archive. */
export async function verifiedHistory(sport:EngineSport,now=new Date()){
 const archive=await getVerifiedResearchGames(sport);
 return {provider:archive.provider,games:uniqueCompletedGames(archive.games,now)};
}
